# ui/question_upload.py

# Import Streamlit to build and display the user interface.
import streamlit as st


def render_question_upload_section(question_df, followup_cols):
    """
    Render the question upload preview section.

    This function:
    - shows the uploaded research questions,
    - displays detected follow-up columns,
    - provides a button to run all questions,
    - returns whether the run button was clicked.

    Args:
        question_df: A pandas DataFrame containing the uploaded questions.
        followup_cols: A list of column names that contain follow-up questions.

    Returns:
        bool: True if the user clicked RUN ALL QUESTIONS, otherwise False.
    """

    # Start a styled section box.
    # The "section-box" CSS class should be defined in the app's global styles.
    st.markdown(
        '<div class="section-box">',
        unsafe_allow_html=True,
    )

    # Display the section title.
    # The "section-title" CSS class should also be defined in the app's styles.
    st.markdown(
        '<div class="section-title"> Batch Research Questions </div>',
        unsafe_allow_html=True,
    )

    # Check whether a valid question dataframe has been loaded.
    if question_df is not None and not question_df.empty:

        # Show a success message with the number of loaded research questions.
        st.success(f"Loaded {len(question_df)} research questions.")

        # Display the uploaded question dataframe in the app.
        st.dataframe(
            question_df,
            use_container_width=True,
        )

        # Convert detected follow-up column names into a readable string.
        # If there are no follow-up columns, display "None".
        detected = ", ".join(followup_cols) if followup_cols else "None"

        # Show the detected follow-up columns as a small note.
        st.markdown(
            f"<div class='small-note'>Detected follow-up columns: {detected}</div>",
            unsafe_allow_html=True,
        )

        # Create the main button used to start running all questions.
        # The result is True only when the button is clicked.
        run_clicked = st.button(
            "RUN ALL QUESTIONS",
            type="primary",
            use_container_width=True,
            key="run_all_btn",
        )

    else:
        # If no valid question file has been uploaded yet, show an information message.
        st.info("Upload a question CSV / TSV to begin.")

        # No run should happen when there is no question data.
        run_clicked = False

    # Close the styled section box.
    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )

    # Return whether the user clicked the run button.
    return run_clicked