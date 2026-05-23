# app.py

# Import Streamlit to build and run the web app.
import streamlit as st

# Import project configuration values.
# COMBINED_DIR is where combined output CSV files are stored.
# FIXED_INDEX_DIR is the folder containing the fixed saved index.
# REQUIRED_INDEX_FILES lists the files needed for the fixed index to be valid.
from config import COMBINED_DIR, FIXED_INDEX_DIR, REQUIRED_INDEX_FILES

# Import the helper function that sets default Streamlit session-state values.
from state import init_session_state

# Import UI rendering functions.
# Each function is responsible for one part of the app interface.
from ui.styles import apply_global_styles
from ui.overview import render_project_overview
from ui.sidebar import render_sidebar
from ui.question_upload import render_question_upload_section
from ui.batch_summary import render_batch_summary
from ui.downloads import render_downloads
from ui.tables import render_result_tables
from ui.graph_viewer import render_graph_viewer

# Import file utility functions.
# These functions help load uploaded files, validate question data,
# check the saved index, and convert dataframes into downloadable CSV bytes.
from utils.file_utils import (
    load_delimited_upload,
    load_question_csv_from_upload,
    validate_question_df,
    has_real_index_files,
    bytes_from_df,
)

# Import helper functions for displaying metric scores in the UI.
from utils.score_utils import score_color, score_text

# Import service functions used by the app.
# These functions load the index, create the LLM, initialise RAGAS,
# and run the full batch of questions.
from services.index_service import load_fixed_index
from services.llm_service import make_llm
from services.ragas_service import init_ragas
from services.batch_service import run_batch_questions


def main():
    """
    Run the main Streamlit application.

    This function:
    - sets up the page,
    - loads global styles,
    - renders the project overview and sidebar,
    - validates user inputs,
    - loads the Reddit source file and question file,
    - runs the batch process when requested,
    - displays the batch summary, downloads, result table, and graph viewer.
    """

    # -----------------------------
    # App setup
    # -----------------------------

    # Configure the browser tab title, page icon, and app layout.
    st.set_page_config(
        page_title="Dyslexia Knowledge Explorer",
        page_icon="🧠",
        layout="wide",
    )

    # Initialise Streamlit session-state variables.
    # This makes sure required keys exist before the app uses them.
    init_session_state()

    # Apply global CSS styles for the app interface.
    apply_global_styles()

    # Display the main app title.
    st.title("DYSLEXIA KNOWLEDGE GRAPH EXPLORER")

    # Display a short description under the title.
    st.caption(
        "Batch-run all research questions and follow-up queries, "
        "then select any question to preview its graph."
    )

    # Render the project overview section.
    render_project_overview()

    # -----------------------------
    # Sidebar
    # -----------------------------

    # Render the sidebar and collect all user-selected settings.
    sidebar_values = render_sidebar()

    # Extract sidebar values into local variables for easier use.
    api_key = sidebar_values["api_key"]
    raw_csv_file = sidebar_values["raw_csv_file"]
    question_file = sidebar_values["question_file"]
    selected_query_model = sidebar_values["selected_query_model"]
    top_k = sidebar_values["top_k"]
    chunk_sz = sidebar_values["chunk_sz"]
    run_eval = sidebar_values["run_eval"]
    run_evidence_alignment = sidebar_values["run_evidence_alignment"]
    build_graphs_during_batch = sidebar_values["build_graphs_during_batch"]
    save_graph_png = sidebar_values["save_graph_png"]

    # -----------------------------
    # Input validation
    # -----------------------------

    # Stop the app until the user enters an OpenRouter API key.
    if not api_key:
        st.info("👈 Enter your OpenRouter API key in the sidebar.")
        st.stop()

    # Do a simple length check to catch clearly invalid API keys.
    if len(api_key.strip()) < 10:
        st.error("That does not look like a valid OpenRouter API key.")
        st.stop()

    # Stop the app until the user selects a query-time model.
    if not selected_query_model:
        st.info("👈 Select a query-time LLM in the sidebar.")
        st.stop()

    # Stop the app until the user uploads the Reddit source CSV.
    if raw_csv_file is None:
        st.error("Please upload the Reddit source CSV.")
        st.stop()

    # Check that the fixed index folder exists and contains the required files.
    # The app cannot run queries without this fixed property graph index.
    if not has_real_index_files(FIXED_INDEX_DIR):
        st.error(
            f"Fixed index folder is missing or incomplete: `{FIXED_INDEX_DIR}`\n\n"
            f"Expected files: {', '.join(REQUIRED_INDEX_FILES)}"
        )
        st.stop()

    # -----------------------------
    # Load Reddit source CSV
    # -----------------------------

    # Try to load the uploaded Reddit source file.
    # The file may be CSV, TSV, or another delimited text file.
    try:
        raw_df = load_delimited_upload(raw_csv_file)
    except Exception as e:
        st.error(f"Failed to load Reddit source CSV: {e}")
        st.stop()

    # Clean column names by converting them to strings and removing extra spaces.
    raw_df.columns = [str(c).strip() for c in raw_df.columns]

    # Make sure the required source columns exist.
    # reddit_id is used to link retrieved chunks back to the original post.
    # text_cleaned stores the cleaned Reddit text.
    if "reddit_id" not in raw_df.columns or "text_cleaned" not in raw_df.columns:
        st.error("Reddit source CSV must contain `reddit_id` and `text_cleaned` columns.")
        st.stop()

    # Convert reddit_id values to clean strings for reliable matching later.
    raw_df["reddit_id"] = raw_df["reddit_id"].astype(str).str.strip()

    # -----------------------------
    # Load question CSV
    # -----------------------------

    # If the user uploaded a question file, load and validate it.
    if question_file is not None:
        try:
            # Load the question file from upload.
            question_df = load_question_csv_from_upload(question_file)

            # Validate the question dataframe and detect follow-up columns.
            question_df, followup_cols = validate_question_df(question_df)

            # Store the validated question dataframe in session state.
            # This allows the data to persist across Streamlit reruns.
            st.session_state.question_df = question_df
            st.session_state.followup_cols = followup_cols

        except Exception as e:
            # Show validation or loading errors to the user.
            st.error(str(e))
            st.stop()

    # -----------------------------
    # Question upload section
    # -----------------------------

    # Render the question preview section.
    # This section also includes the RUN ALL QUESTIONS button.
    run_clicked = render_question_upload_section(
        question_df=st.session_state.question_df,
        followup_cols=st.session_state.followup_cols,
    )

    # Stop the app if no valid question data is available.
    if st.session_state.question_df is None or st.session_state.question_df.empty:
        st.stop()

    # If the user clicked RUN ALL QUESTIONS, mark the run request
    # and rerun the app so the batch process starts cleanly.
    if run_clicked:
        st.session_state.run_requested = True
        st.rerun()

    # -----------------------------
    # Run batch
    # -----------------------------

    # Run the batch only when requested by the user.
    if st.session_state.run_requested:

        # Reset the request flag so the batch does not run repeatedly
        # on every Streamlit rerun.
        st.session_state.run_requested = False

        # Load the fixed property graph index.
        try:
            index = load_fixed_index(api_key, selected_query_model)
        except Exception as e:
            st.error(f"Failed to load fixed index: {e}")
            st.stop()

        # Create the LLM used for answer generation and follow-up answering.
        current_llm = make_llm(selected_query_model, api_key)

        # Initialise RAGAS only if evaluation is enabled.
        if run_eval:
            try:
                init_ragas(
                    api_key=api_key,
                    eval_model=selected_query_model,
                )
            except Exception as e:
                st.warning(
                    f"RAGAS initialisation failed. Evaluation may fail. Error: {e}"
                )

        # Run all main research questions and follow-up questions.
        try:
            # Show a spinner while the batch process is running.
            with st.spinner("Running all research questions and follow-ups..."):
                batch_results = run_batch_questions(
                    index=index,
                    raw_df=raw_df,
                    llm=current_llm,
                    question_df=st.session_state.question_df,
                    followup_cols=st.session_state.followup_cols,
                    query_llm_model=selected_query_model,
                    top_k=top_k,
                    chunk_sz=chunk_sz,
                    run_eval=run_eval,
                    run_evidence_alignment=run_evidence_alignment,
                    save_graph_png=save_graph_png,
                    build_graphs_during_batch=build_graphs_during_batch,
                )

            # Store the batch results in session state so they remain available
            # after the app reruns.
            st.session_state.batch_results = batch_results

            # Show saved output locations to the user.
            st.success(f"Batch saved to: {batch_results['batch_dir']}")
            st.info(f"Combined CSVs updated in: {COMBINED_DIR}")
            st.info(
                "Graph screenshots folder: "
                f"{batch_results['batch_manifest'].get('graph_screenshots_dir', 'N/A')}"
            )

        except Exception as e:
            # Show a clear error if the batch process fails.
            st.error("Batch run failed.")
            st.exception(e)
            st.stop()

    # -----------------------------
    # Stop if no batch results yet
    # -----------------------------

    # If the user has not run a batch yet, stop before rendering result sections.
    if not st.session_state.batch_results:
        st.stop()

    # Get the stored batch results.
    batch_results = st.session_state.batch_results

    # Extract the combined results dataframe and the list of main-question results.
    all_results_df = batch_results["all_results_df"]
    main_results_by_question = batch_results.get("main_results_by_question", [])

    # -----------------------------
    # Batch summary
    # -----------------------------

    # Render the batch summary cards and saved path information.
    render_batch_summary(batch_results)

    # -----------------------------
    # Downloads
    # -----------------------------

    # Render the CSV download section.
    render_downloads(
        all_results_df=all_results_df,
        bytes_from_df=bytes_from_df,
    )

    # -----------------------------
    # Result tables
    # -----------------------------

    # Render the all-results dataframe table.
    render_result_tables(
        all_results_df=all_results_df,
    )

    # -----------------------------
    # Graph viewer
    # -----------------------------

    # Render the interactive graph viewer and metric cards.
    render_graph_viewer(
        main_results_by_question=main_results_by_question,
        score_color=score_color,
        score_text=score_text,
    )


# Run the app only when this file is executed directly.
if __name__ == "__main__":
    main()