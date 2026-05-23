# ui/graph_viewer.py

# Import regular expressions.
# This is used to find citation markers such as [1], [2], and highlight them.
import re

# Import Streamlit for building the user interface.
import streamlit as st

# Import Streamlit components.
# This is used to render the interactive graph HTML inside the app.
import streamlit.components.v1 as components


def render_graph_viewer(
    main_results_by_question,
    score_color,
    score_text,
):
    """
    Render the question graph viewer section in the Streamlit app.

    This function allows the user to:
    - select a completed research question,
    - view its generated answer,
    - see citation markers highlighted,
    - inspect graph diagnostic information,
    - view the generated knowledge graph,
    - view RAGAS metric scores for the selected answer.

    Args:
        main_results_by_question: A list of dictionaries containing main question results.
        score_color: A helper function that returns a colour based on the metric score.
        score_text: A helper function that formats the metric score for display.
    """

    # If no main question results are available, do not render anything.
    # This prevents errors before a batch run has been completed.
    if not main_results_by_question:
        return

    # Start a styled section box.
    # The class "section-box" should be defined in the app's CSS.
    st.markdown(
        '<div class="section-box">',
        unsafe_allow_html=True,
    )

    # Display the section title.
    # The class "section-title" should be defined in the app's CSS.
    st.markdown(
        '<div class="section-title"> Question Graph Viewer </div>',
        unsafe_allow_html=True,
    )

    # Show a dropdown list so the user can choose which question to preview.
    selected_item = st.selectbox(
        "Select a research question to preview",

        # Each option is one completed main question result.
        options=main_results_by_question,

        # Format each dropdown option in a readable way.
        # Example: Q1 | RQ1 — What barriers do dyslexic students report?
        format_func=lambda item: (
            f"Q{item['question_index']} | "
            f"{item['question_id']} — "
            f"{item['query']}"
        ),

        # Unique Streamlit key for this selectbox.
        key="graph_viewer_question",
    )

    # If no question is selected, show an information message and stop.
    if not selected_item:
        st.info("Please select the question number to see its graph.")
        return

    # Extract the main result dictionary for the selected question.
    selected_main_result = selected_item["main_result"]

    # Extract graph debugging information if it exists.
    # This can show why a graph was or was not created.
    selected_graph_debug = selected_main_result.get("graph_debug", {})

    # Display metadata about the selected question.
    st.markdown(f"**Question ID:** `{selected_item['question_id']}`")
    st.markdown(f"**Research Question:** {selected_item['query']}")
    st.markdown(f"**Saved folder:** `{selected_item.get('question_dir', 'N/A')}`")
    st.markdown(
        f"**Graph screenshot status:** "
        f"`{selected_item.get('graph_screenshot_status', 'N/A')}`"
    )

    # If a graph PNG file was saved, display its file path.
    if selected_item.get("graph_png_file"):
        st.markdown(f"**Graph PNG file:** `{selected_item['graph_png_file']}`")

    # If graph diagnostics are available, show them as formatted JSON.
    if selected_graph_debug:
        st.markdown("**Graph diagnostics:**")
        st.json(selected_graph_debug)

    # Highlight citation markers in the answer.
    # For example, [1] becomes a styled badge using the "badge" CSS class.
    highlighted_answer = re.sub(
        r"\[(\d+)\]",
        r'<span class="badge">[\1]</span>',
        selected_main_result["response_text"],
    )

    # Display the generated answer with highlighted citations.
    # unsafe_allow_html=True is required because the citation badges use HTML.
    st.markdown(
        f'<div class="answer-text">{highlighted_answer}</div>',
        unsafe_allow_html=True,
    )

    # If graph HTML exists, render the interactive knowledge graph.
    if selected_main_result["graph_html"]:
        st.markdown("### Knowledge Graph")

        # Render the graph HTML inside the Streamlit app.
        # The height controls how much vertical space the graph uses.
        components.html(
            selected_main_result["graph_html"],
            height=900,
            scrolling=False,
        )

    else:
        # If graph building was turned off, explain why no graph is shown.
        if selected_graph_debug.get("build_graph") is False:
            st.info(
                "Graph was not built during the batch run. "
                "Turn on 'Build graphs during batch' in the sidebar "
                "if you want graphs for every question."
            )

        # If graph building was enabled but no graph exists, show a general message.
        else:
            st.info("No graph available for this question.")

    # If metric scores are available, display them in metric cards.
    if selected_main_result["metric_scores"]:
        # Add a small visual space before the metric cards.
        st.markdown("<br>", unsafe_allow_html=True)

        # Icons used beside each metric name.
        metric_icons = {
            "Answer Relevancy": "🎯",
            "Faithfulness": "✅",
            "Context Relevance": "📎",
            "Response Groundedness": "🔗",
        }

        # Create four columns, one for each metric.
        cols = st.columns(4)

        # Display each metric score in its own styled card.
        for col, (metric, score) in zip(
            cols,
            selected_main_result["metric_scores"].items(),
        ):
            # Get the display colour for the score.
            color = score_color(score)

            # Render the metric card.
            # score_text() formats None or numeric values into readable text.
            col.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-label">
                        {metric_icons.get(metric, "•")} {metric}
                    </div>
                    <div class="metric-value" style="color:{color};">
                        {score_text(score)}
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    # Close the styled section box.
    st.markdown("</div>", unsafe_allow_html=True)