# Import Streamlit to build the app interface.
import streamlit as st


def render_downloads(
    all_results_df,
    bytes_from_df,
):
    """
    Render the download section of the Streamlit app.

    This function shows a download button for the combined results CSV.
    If no results are available yet, it shows an information message instead.

    Args:
        all_results_df: A pandas DataFrame containing all batch results.
        bytes_from_df: A helper function that converts a DataFrame into CSV bytes.
    """

    # Start a styled section box.
    # The "section-box" class should be defined in the app's global CSS.
    st.markdown(
        '<div class="section-box">',
        unsafe_allow_html=True,
    )

    # Display the section title.
    # The "section-title" class should also be defined in the app's global CSS.
    st.markdown(
        '<div class="section-title"> Download </div>',
        unsafe_allow_html=True,
    )

    # If the results dataframe is empty, show a message instead of a download button.
    if all_results_df.empty:
        st.info("No all_results data available yet.")

    else:
        # Create a download button for the complete results CSV.
        st.download_button(
            # Text shown on the button.
            "⬇️ Download All Results CSV",

            # Convert the dataframe to CSV bytes before downloading.
            data=bytes_from_df(all_results_df),

            # Default filename for the downloaded CSV file.
            file_name="all_results.csv",

            # File type for the download.
            mime="text/csv",

            # Make the button use the full available container width.
            use_container_width=True,
        )

    # Close the styled section box.
    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )