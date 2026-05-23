# ui/batch_summary.py

# Import Streamlit to display UI elements such as markdown, columns, and metrics.
import streamlit as st


def render_batch_summary(batch_results):
    """
    Render a summary section for the completed batch run.

    This function displays:
    - number of questions processed,
    - number of main question runs,
    - number of follow-up runs,
    - the LLM used,
    - batch ID,
    - saved output folder,
    - graph screenshot folder,
    - number of successfully saved graph PNG screenshots.

    Args:
        batch_results: A dictionary returned by the batch processing service.
                       It contains the batch manifest and result dataframes.
    """

    # If there are no batch results yet, do not render anything.
    # This prevents errors when the app loads before a batch has been run.
    if not batch_results:
        return

    # Extract the batch manifest.
    # The manifest contains high-level metadata about the batch run.
    manifest = batch_results["batch_manifest"]

    # Extract the dataframe that summarises all main question runs.
    main_summary_df = batch_results["main_summary_df"]

    # Start a styled HTML section box.
    # The class "section-box" is expected to be styled in the global CSS.
    st.markdown(
        '<div class="section-box">',
        unsafe_allow_html=True,
    )

    # Display the section title.
    # The class "section-title" is expected to be styled in the global CSS.
    st.markdown(
        '<div class="section-title"> Batch Summary </div>',
        unsafe_allow_html=True,
    )

    # Create four columns for showing key batch metrics side by side.
    c1, c2, c3, c4 = st.columns(4)

    # Display the total number of questions in the uploaded question file.
    c1.metric("Questions", manifest["num_questions"])

    # Display the number of main research question runs completed.
    c2.metric("Main runs", manifest["num_main_runs"])

    # Display the number of follow-up question runs completed.
    c3.metric("Follow-up runs", manifest["num_followup_runs"])

    # Display the LLM model used for this batch run.
    c4.metric("LLM", manifest["query_llm_model"])

    # Display the unique batch ID.
    # This helps users trace saved files back to a specific run.
    st.markdown(f"**Batch ID:** `{manifest['batch_id']}`")

    # Display the folder where this batch output was saved.
    st.markdown(f"**Saved folder:** `{manifest['saved_dir']}`")

    # Display the graph screenshot folder.
    # If the value is missing, show N/A.
    st.markdown(
        f"**Graph screenshots folder:** "
        f"`{manifest.get('graph_screenshots_dir', 'N/A')}`"
    )

    # Check whether the main summary dataframe has graph screenshot status data.
    # If available, count how many graph PNG screenshots were saved successfully.
    if (
        not main_summary_df.empty
        and "graph_screenshot_status" in main_summary_df.columns
    ):
        # Count rows where the graph screenshot status is "Saved".
        saved_count = (
            main_summary_df["graph_screenshot_status"] == "Saved"
        ).sum()

        # Display the number of saved graph screenshots out of all main runs.
        st.markdown(
            f"**Saved graph PNG screenshots:** "
            f"`{int(saved_count)}` / `{len(main_summary_df)}`"
        )

    # Close the styled HTML section box.
    st.markdown("</div>", unsafe_allow_html=True)