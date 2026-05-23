# services/graph_service.py

# Import tempfile to create short-term temporary files.
# This is used when saving graph HTML before taking a screenshot.
import tempfile

# Import Counter to count repeated triples, nodes, and graph connections.
from collections import Counter

# Import Path for safe file path handling.
from pathlib import Path

# Import Optional for type hints where a function may return None.
from typing import Optional

# Import pandas to work with trace dataframes.
import pandas as pd

# Import PyVis Network to create interactive HTML network graphs.
from pyvis.network import Network

# Import the colour palette used for graph nodes.
from config import PALETTE


def get_triples_from_nodes(nodes) -> list[tuple]:
    """
    Extract knowledge graph triples from retrieved source nodes.

    Expected triple format inside node text:
        subject -> relation -> object

    Args:
        nodes: A list of retrieved nodes. Each node may store text in
               node.node.text or node.text depending on the object type.

    Returns:
        A list of triples as tuples:
        [
            ("subject", "relation", "object"),
            ...
        ]
    """

    # Store all parsed triples.
    triples = []

    # Go through each retrieved node.
    for node in nodes:
        raw_text = ""

        # Some LlamaIndex objects store the actual text inside node.node.text.
        if hasattr(node, "node") and hasattr(node.node, "text"):
            raw_text = node.node.text or ""

        # Other node objects may store the text directly as node.text.
        elif hasattr(node, "text"):
            raw_text = node.text or ""

        # Read the node text line by line.
        for line in str(raw_text).splitlines():
            line = line.strip()

            # Split lines that follow the expected triple format.
            parts = line.split(" -> ")

            # Only keep lines that have exactly three parts:
            # subject, relation, and object.
            if len(parts) == 3:
                triples.append(tuple(p.strip() for p in parts))

    # Return all triples found in the nodes.
    return triples


def trace_triple_to_source(index, subject: str, relation: str, obj: str) -> list[dict]:
    """
    Trace a graph triple back to the original source text in the property graph.

    This helps explain where a triple came from by finding graph nodes that
    contain the subject and object terms.

    Args:
        index: The property graph index.
        subject: The subject part of the triple.
        relation: The relation part of the triple.
        obj: The object part of the triple.

    Returns:
        A list of dictionaries containing the matched source details.
    """

    # Get all nodes from the property graph store.
    all_nodes = list(index.property_graph_store.graph.nodes.values())

    # Store matched source records.
    results = []

    # Search through each graph node.
    for node in all_nodes:
        # Try to get the text from the node.
        # If text is not available, use the label.
        text = getattr(node, "text", "") or getattr(node, "label", "") or ""

        # Get the Reddit ID from the node properties if available.
        reddit_id = node.properties.get("reddit_id")

        # Skip nodes that have no searchable text.
        if not text:
            continue

        # Check whether both the subject and object appear in the node text.
        # This is a simple case-insensitive matching approach.
        if subject.lower() in text.lower() and obj.lower() in text.lower():

            # Extract sentences that mention the subject or object.
            matched = [
                s.strip()
                for s in text.split(".")
                if s.strip()
                and (
                    subject.lower() in s.lower()
                    or obj.lower() in s.lower()
                )
            ]

            # Save the trace record.
            results.append({
                "reddit_id": reddit_id,
                "subject": subject,
                "relation": relation,
                "object": obj,
                "triple": f"{subject} -- ({relation}) -- {obj}",
                "matched_sentences": " | ".join(matched),
                "text_cleaned": text,
            })

    # Return all matched source records for this triple.
    return results


def build_graph_html(
    triples: list[tuple],
    trace_df: Optional[pd.DataFrame] = None,
) -> str:
    """
    Build an interactive HTML graph from knowledge graph triples.

    The graph:
    - Creates one node for each subject and object.
    - Creates directed edges for relations.
    - Counts repeated triples.
    - Sizes nodes based on how often they appear.
    - Colours nodes using the project palette.

    Args:
        triples: A list of triples in the format:
                 (subject, relation, object)
        trace_df: Optional dataframe containing traced triples and source records.

    Returns:
        An HTML string generated by PyVis.
    """

    # Store assigned colours for graph labels.
    # This keeps each label colour consistent within the graph.
    color_map = {}

    def get_color(label: str) -> str:
        """
        Assign and return a colour for a graph node label.

        If the label already has a colour, reuse it.
        Otherwise, assign the next colour from the palette.
        """

        if label not in color_map:
            color_map[label] = PALETTE[len(color_map) % len(PALETTE)]

        return color_map[label]

    # Create the PyVis network object.
    net = Network(
        height="950px",
        width="100%",
        bgcolor="#FFFFFF",
        font_color="#01090b",
        directed=True,
        cdn_resources="in_line",
    )

    # Set the graph layout physics.
    # Barnes-Hut helps spread nodes in a readable way.
    net.barnes_hut(
        gravity=-8000,
        central_gravity=0.3,
        spring_length=120,
    )

    # If trace data is available, count triples using the trace dataframe.
    # This is useful when the same triple appears in multiple source records.
    if trace_df is not None and not trace_df.empty:
        grp = (
            trace_df.groupby(["subject", "relation", "object"], sort=False)
            .size()
            .reset_index(name="count")
        )

        edge_counts = {
            (row.subject, row.relation, row.object): int(row.count)
            for row in grp.itertuples()
        }

    # If no trace data is available, count repeated triples directly.
    else:
        edge_counts = Counter(triples)

    # Count how often each node appears in the graph.
    node_counts = Counter()

    for (s, r, o), cnt in edge_counts.items():
        node_counts[s] += cnt
        node_counts[o] += cnt

    # Find the highest node count.
    # This is used to scale node sizes.
    max_count = max(node_counts.values(), default=1)

    def get_node_size(
        label: str,
        min_size: int = 15,
        max_size: int = 60,
    ) -> int:
        """
        Calculate node size based on how often the node appears.

        More frequent nodes become larger.
        Less frequent nodes stay closer to the minimum size.
        """

        if max_count == 1:
            return min_size

        return int(
            min_size
            + (node_counts[label] / max_count) * (max_size - min_size)
        )

    # Keep track of nodes that have already been added.
    # This prevents duplicate nodes in the graph.
    added = set()

    # Add graph nodes and edges.
    for (subject, relation, obj), count in edge_counts.items():

        # Add the subject node if it has not already been added.
        if subject not in added:
            net.add_node(
                subject,
                label=subject,
                color=get_color(subject),
                size=get_node_size(subject),
                title=f"{subject}\nMentions: {node_counts[subject]}",
            )
            added.add(subject)

        # Add the object node if it has not already been added.
        if obj not in added:
            net.add_node(
                obj,
                label=obj,
                color=get_color(obj),
                size=get_node_size(obj),
                title=f"{obj}\nMentions: {node_counts[obj]}",
            )
            added.add(obj)

        # Add a directed edge from subject to object.
        # The edge label shows the relation and occurrence count.
        net.add_edge(
            subject,
            obj,
            label=f"{relation} ({count})",
            color="#CCCCCC",
            font_color="#000006",
            width=1 + count * 0.5,
            title=f"{relation}\nOccurrences: {count}",
        )

    # Generate and return the full HTML for the interactive graph.
    return net.generate_html()


def save_graph_screenshot_from_html(
    html_content: str,
    output_png_path: Path,
    width: int = 1600,
    height: int = 1200,
    wait_ms: int = 2500,
) -> Optional[str]:
    """
    Save a PNG screenshot from generated graph HTML.

    This function:
    - Writes the HTML into a temporary file.
    - Opens it in a headless Chromium browser using Playwright.
    - Waits for the graph to render.
    - Captures a screenshot as a PNG file.

    Args:
        html_content: The graph HTML content.
        output_png_path: The path where the PNG screenshot should be saved.
        width: Browser viewport width.
        height: Browser viewport height.
        wait_ms: Waiting time in milliseconds before taking the screenshot.

    Returns:
        None if the screenshot is saved successfully.
        A string error message if something fails.
    """

    # Do not continue if there is no HTML content to render.
    if not html_content:
        return "No HTML content provided."

    # Import Playwright only when this function is called.
    # This avoids requiring Playwright unless screenshot saving is needed.
    try:
        from playwright.sync_api import sync_playwright
    except Exception as e:
        return f"Playwright not available: {e}"

    # Make sure the output folder exists.
    output_png_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        # Create a temporary folder to store the HTML file.
        with tempfile.TemporaryDirectory() as tmpdir:
            html_path = Path(tmpdir) / "graph.html"

            # Write the HTML content into the temporary file.
            html_path.write_text(html_content, encoding="utf-8")

            # Open the temporary HTML file in a headless browser.
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)

                # Create a browser page with the selected viewport size.
                page = browser.new_page(
                    viewport={"width": width, "height": height},
                    device_scale_factor=2,
                )

                # Load the local HTML file.
                page.goto(html_path.as_uri(), wait_until="load")

                # Wait so the PyVis graph has time to render fully.
                page.wait_for_timeout(wait_ms)

                # Save a screenshot of the rendered graph.
                page.screenshot(
                    path=str(output_png_path),
                    full_page=True,
                )

                # Close the browser after the screenshot is saved.
                browser.close()

        # None means the screenshot was saved successfully.
        return None

    except Exception as e:
        # Return the error message so the caller can display or save it.
        return f"Failed to capture screenshot: {e}"