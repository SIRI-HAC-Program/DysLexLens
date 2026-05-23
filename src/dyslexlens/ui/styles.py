# ui/styles.py

# Import Streamlit to inject custom CSS into the app.
import streamlit as st


def apply_global_styles():
    """
    Apply global CSS styles to the Streamlit app.

    This function controls the main visual design of the app, including:
    - dark background colour,
    - section boxes,
    - hero banner,
    - information cards,
    - answer text,
    - citation badges,
    - metric cards,
    - small helper notes.

    The CSS is injected using st.markdown with unsafe_allow_html=True.
    """

    # Inject custom CSS into the Streamlit app.
    # unsafe_allow_html=True is needed because we are passing raw HTML/CSS.
    st.markdown(
        """
        <style>
            /* Keep download button text dark and readable. */
            .stDownloadButton button {
                color: #111111 !important;
            }

            /* Keep the same readable colour when the download button is hovered. */
            .stDownloadButton button:hover {
                color: #111111 !important;
            }

            /* Set the main app background and default text colour. */
            .stApp {
                background-color: #0f1117;
                color: #e0e0e0;
            }

            /* Reduce the default top spacing of the Streamlit page container. */
            .block-container {
                padding-top: 1.5rem;
            }

            /* Style reusable content sections throughout the app. */
            .section-box {
                background: #1a1a2e;
                border: 1px solid #2a2a3e;
                border-radius: 12px;
                padding: 20px;
                margin-bottom: 20px;
            }

            /* Style small section labels shown at the top of each section box. */
            .section-title {
                color: #9aa0b4;
                font-size: 11px;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 10px;
            }

            /* Style the main hero banner at the top of the app. */
            .hero-box {
                background: linear-gradient(135deg, #171a2c 0%, #1f2440 100%);
                border: 1px solid #2a2a3e;
                border-radius: 16px;
                padding: 24px;
                margin-bottom: 20px;
            }

            /* Style the main app title inside the hero banner. */
            .hero-title {
                font-size: 34px;
                font-weight: 800;
                margin-bottom: 8px;
                color: #ffffff;
            }

            /* Style the subtitle text inside the hero banner. */
            .hero-subtitle {
                font-size: 16px;
                color: #c9c9d4;
                line-height: 1.7;
            }

            /* Style information cards used in the overview section. */
            .info-card {
                background: #151829;
                border: 1px solid #2a2a3e;
                border-radius: 12px;
                padding: 18px;
                height: 100%;
            }

            /* Style headings inside information cards. */
            .info-card h4 {
                margin-top: 0;
                margin-bottom: 10px;
                color: #ffffff;
            }

            /* Style paragraph and list text inside information cards. */
            .info-card p,
            .info-card li {
                color: #d4d4dc;
                line-height: 1.7;
                font-size: 14px;
            }

            /* Style generated answer text. */
            .answer-text {
                color: #e0e0e0;
                font-size: 14px;
                line-height: 1.8;
            }

            /* Style citation badges such as [1], [2], and [3]. */
            .badge {
                background: #534AB7;
                color: white;
                padding: 1px 8px;
                border-radius: 10px;
                font-size: 12px;
                font-weight: bold;
            }

            /* Style metric score cards used for RAGAS scores. */
            .metric-card {
                background: #12121f;
                border: 1px solid #2a2a3e;
                border-radius: 8px;
                padding: 16px;
                text-align: center;
            }

            /* Style the small label text inside metric cards. */
            .metric-label {
                font-size: 11px;
                color: #888;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 8px;
            }

            /* Style the large numeric value inside metric cards. */
            .metric-value {
                font-size: 28px;
                font-weight: bold;
            }

            /* Style small helper notes shown in the interface. */
            .small-note {
                color: #aaa;
                font-size: 12px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )