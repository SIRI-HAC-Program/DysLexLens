# Import Streamlit to display UI elements such as markdown, info messages, and dataframes.
import streamlit as st


def render_result_tables(
    all_results_df,
):
    """
    Render the all-results table section in the Streamlit app.

    This function:
    - creates a styled section box,
    - displays the all-results dataframe if data is available,
    - shows an information message if there are no result rows.

    Args:
        all_results_df: A pandas DataFrame containing all main and follow-up result rows.
    """

    # Start a styled section box.
    # The "section-box" CSS class should be defined in the app's global styles.
    st.markdown(
        '<div class="section-box">',
        unsafe_allow_html=True,
    )

    # Display the section title.
    # The "section-title" CSS class should also be defined in the app's global styles.
    st.markdown(
        '<div class="section-title"> All Results </div>',
        unsafe_allow_html=True,
    )

    # If the dataframe has no rows, show an information message.
    if all_results_df.empty:
        st.info("No all_results rows.")

    else:
        # Display the complete results dataframe in the app.
        # use_container_width=True makes the table fit the available page width.
        st.dataframe(
            all_results_df,
            use_container_width=True,
        )

    # Close the styled section box.
    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )