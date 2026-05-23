# ui/sidebar.py

# Import Streamlit to build the sidebar UI.
import streamlit as st

# Import project configuration values used in the sidebar.
from config import (
    FIXED_INDEX_DIR,
    FIXED_INDEX_LLM_MODEL,
    FIXED_EMBED_MODEL,
    OPENROUTER_MODELS,
)


def render_sidebar():
    """
    Render the Streamlit sidebar and collect all user configuration inputs.

    This function allows the user to:
    - enter the OpenRouter API key,
    - upload the Reddit source CSV,
    - upload the research question CSV or TSV,
    - view the fixed index configuration,
    - select the query-time LLM,
    - configure retrieval and citation settings,
    - choose whether to run evaluation, evidence alignment, and graph generation.

    Returns:
        dict: A dictionary containing all sidebar values needed by the main app.
    """

    # Place all controls inside the Streamlit sidebar.
    with st.sidebar:

        # Display the sidebar heading.
        st.header("⚙️ Configuration")

        # Ask the user to enter their OpenRouter API key.
        # The key is hidden because type="password" is used.
        # The value is stored only in Streamlit session state.
        api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            placeholder="sk-or-...",
            value=st.session_state.get("api_key_input", ""),
            key="api_key_input",
            help="Stored in session only.",
        )

        # Upload the Reddit source data file.
        # This file must contain the original Reddit records used for evidence tracing.
        raw_csv_file = st.file_uploader(
            "Upload Reddit source CSV",
            type=["csv", "tsv", "txt"],
            help="Must contain at least: reddit_id, text_cleaned",
        )

        # Upload the research questions file.
        # This can include main questions and follow-up questions.
        question_file = st.file_uploader(
            "Upload question CSV / TSV",
            type=["csv", "tsv", "txt"],
            help=(
                "Expected columns: question_id, research_question, "
                "followup_1, followup_2, followup_3, ..."
            ),
        )

        # Add a divider to visually separate upload settings from index settings.
        st.divider()

        # Display the fixed index configuration.
        # The fixed index is already built and saved on disk.
        st.subheader("Fixed Index Configuration")

        # Show the saved index folder path.
        st.code(str(FIXED_INDEX_DIR), language=None)

        # Show which models were used to build the fixed index.
        # These are locked to keep retrieval consistent.
        st.caption(
            f"Index locked to:\n"
            f"- Indexing LLM: {FIXED_INDEX_LLM_MODEL}\n"
            f"- Embedding: {FIXED_EMBED_MODEL}"
        )

        # Add another divider before query-time model settings.
        st.divider()

        # Display query-time model settings.
        st.subheader("Query-Time Model Settings")

        # Add a default placeholder option before the available OpenRouter models.
        model_options = ["-- Select a model --"] + OPENROUTER_MODELS

        # Let the user select the LLM used at query time.
        # This model is used for answer generation and related tasks.
        selected_query_model = st.selectbox(
            "Query-time LLM",
            model_options,
            index=0,
            help=(
                "Used only for answer generation, evidence alignment, "
                "follow-up answering, and optional RAGAS evaluation."
            ),
            key="selected_query_model_widget",
        )

        # Convert the placeholder option to None.
        # This makes validation in the main app easier.
        if selected_query_model == "-- Select a model --":
            selected_query_model = None

        # Add a divider before retrieval settings.
        st.divider()

        # Display query and retrieval settings.
        st.subheader("Query Settings")

        # Let the user choose how many similar chunks to retrieve.
        # A higher value may retrieve more evidence but can also add noise.
        top_k = st.slider(
            "Similarity top-k",
            min_value=1,
            max_value=10,
            value=3,
            key="top_k_widget",
        )

        # Let the user choose the citation chunk size.
        # Smaller chunks may give more precise citations.
        # Larger chunks may provide more context.
        chunk_sz = st.slider(
            "Citation chunk size",
            min_value=128,
            max_value=1024,
            value=512,
            step=128,
            key="chunk_sz_widget",
        )

        # Let the user choose whether to run RAGAS evaluation.
        # This adds quality scores but makes the batch slower.
        run_eval = st.checkbox(
            "Run quality eval (RAGAS)",
            value=True,
            key="run_eval_widget",
        )

        # Let the user choose whether to run evidence alignment.
        # Evidence alignment tries to link generated claims to exact supporting text.
        run_evidence_alignment = st.checkbox(
            "Run evidence alignment",
            value=False,
            key="run_evidence_alignment_widget",
        )

        # Let the user choose whether graphs should be built for all questions.
        # This can be useful, but it may slow down the batch process.
        build_graphs_during_batch = st.checkbox(
            "Build graphs during batch",
            value=False,
            key="build_graphs_during_batch_widget",
            help=(
                "Turn this on only if you need graph HTML/PNG files for every question. "
                "Leaving it off makes the batch faster."
            ),
        )

        # Let the user choose whether to save graph PNG screenshots.
        # This option is disabled unless graph building is enabled.
        save_graph_png = st.checkbox(
            "Save graph PNG screenshots",
            value=False,
            key="save_graph_png_widget",
            disabled=not build_graphs_during_batch,
        )

    # Return all sidebar values in one dictionary.
    # The main app uses this dictionary to run validation and batch processing.
    return {
        "api_key": api_key,
        "raw_csv_file": raw_csv_file,
        "question_file": question_file,
        "selected_query_model": selected_query_model,
        "top_k": top_k,
        "chunk_sz": chunk_sz,
        "run_eval": run_eval,
        "run_evidence_alignment": run_evidence_alignment,
        "save_graph_png": save_graph_png,
        "build_graphs_during_batch": build_graphs_during_batch,
    }