# ui/overview.py

# Import Streamlit to build and display the app interface.
import streamlit as st


def render_project_overview():
    """
    Render the project overview section of the Streamlit app.

    This function displays:
    - the main project title,
    - a short project description,
    - the research team,
    - a simple explanation of knowledge graphs,
    - how the app uses the knowledge graph for dyslexia-related Reddit data.
    """

    # Display the main hero section at the top of the app.
    # The HTML classes used here, such as "hero-box", "hero-title", and
    # "hero-subtitle", should be defined in the app's global CSS file.
    st.markdown(
        """
        <div class="hero-box">
            <div class="hero-title">DysLexLens: Dyslexia Knowledge Graph Explorer</div>
            <div class="hero-subtitle">
                SIRI Grant Project — Knowledge Graph–Driven Analysis of Dyslexia-Related Online Discourse.
                This app batch-runs research questions and follow-up queries against a fixed property graph index,
                retrieves evidence-backed answers, evaluates them with RAGAS, saves outputs, and lets you
                preview the graph for any specific question after the batch run finishes.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Create three columns to organise the overview cards side by side.
    col1, col2, col3 = st.columns(3)

    # First card: show the project research team.
    with col1:
        st.markdown(
            """
            <div class="info-card">
                <h4>👥 Research Team</h4>
                <ul>
                    <li>Dr Dana Rezazadegan</li>
                    <li>Dr Young-Bin Kang</li>
                    <li>Dr Atie Kia</li>
                    <li>Dr Dominique Carlon</li>
                    <li>Dr Abhik Banerjee</li>
                    <li>Dr Jeremy Nguyen</li>
                    <li>Dr James George Marshall</li>
                    <li>RA: Bay Nandavong</li>
                </ul>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Second card: explain what a knowledge graph is in simple terms.
    with col2:
        st.markdown(
            """
            <div class="info-card">
                <h4>🧠 What is a Knowledge Graph?</h4>
                <p>
                    A knowledge graph represents information as interconnected entities (nodes) and relationships (edges).
                    It supports structured reasoning, evidence tracing, and more explainable analysis over complex text collections.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )

    # Third card: explain how the knowledge graph is used in this project.
    with col3:
        st.markdown(
            """
            <div class="info-card">
                <h4>📌 How It Is Used Here</h4>
                <p>
                    This project uses a fixed property graph built from Reddit discussions about dyslexia.
                    The app answers research questions by querying the graph, retrieving cited evidence,
                    and supporting analysis of concepts, challenges, strategies, and lived experiences.
                </p>
            </div>
            """,
            unsafe_allow_html=True,
        )