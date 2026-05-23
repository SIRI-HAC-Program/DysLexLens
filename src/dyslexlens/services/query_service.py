# services/query_service.py

# Import asyncio to run asynchronous RAGAS scoring from normal synchronous code.
import asyncio

# Import time to measure how long each answer generation takes.
import time

# Import uuid to create unique IDs for each main and follow-up query run.
import uuid

# Import pandas for creating dataframes, especially for graph trace data.
import pandas as pd

# Import the LlamaIndex citation query engine.
# This engine returns answers with citation markers and source nodes.
from llama_index.core.query_engine import CitationQueryEngine

# Import evidence-related helper functions.
# align_evidence_for_response checks which cited chunks support each answer sentence.
# ask_followup_with_citation answers follow-up questions using labelled context chunks.
from services.evidence_service import (
    align_evidence_for_response,
    ask_followup_with_citation,
)

# Import graph-related helper functions.
# These are used to extract triples, trace them back to sources, and build graph HTML.
from services.graph_service import (
    get_triples_from_nodes,
    trace_triple_to_source,
    build_graph_html,
)

# Import the RAGAS scoring function used to evaluate generated answers.
from services.ragas_service import scoring_metric

# Import text helper functions.
# get_used_citations extracts citation numbers like [1], [2].
# get_used_subquery_citations extracts follow-up citations like [C1], [C2].
# strip_kg_triples removes knowledge graph triple text from retrieved chunks.
from utils.text_utils import (
    get_used_citations,
    get_used_subquery_citations,
    strip_kg_triples,
)

# Import helper function to create timestamps in ISO format.
from utils.time_utils import iso_now

# Import the main question-answering prompt template.
from prompts.templates import MAIN_QA_PROMPT


def prepare_ragas_contexts(
    nodes,
    max_contexts: int = 3,
    max_chars_per_context: int = 1500,
) -> list[str]:
    """
    Prepare shorter and cleaner contexts for RAGAS evaluation.

    RAGAS can fail or become slow if the retrieved context is too long.
    This function keeps only a limited number of source nodes and trims
    each context to a maximum number of characters.

    Args:
        nodes: Retrieved source nodes from LlamaIndex.
        max_contexts: Maximum number of context chunks to use.
        max_chars_per_context: Maximum number of characters per context chunk.

    Returns:
        A list of cleaned and shortened context strings.
    """

    # Store cleaned context chunks.
    contexts = []

    # Use only the first few retrieved nodes to keep evaluation manageable.
    for node in nodes[:max_contexts]:

        # LlamaIndex nodes may store text in node.node.text or node.text.
        raw_text = node.node.text if hasattr(node, "node") else node.text

        # Remove knowledge graph triples and trim extra spaces.
        clean_text = strip_kg_triples(raw_text).strip()

        # Only keep non-empty text.
        if clean_text:
            contexts.append(clean_text[:max_chars_per_context])

    # Return the cleaned and shortened contexts.
    return contexts


def run_main_query(
    index,
    raw_df,
    llm,
    query: str,
    top_k: int,
    chunk_sz: int,
    run_eval: bool,
    run_evidence_alignment: bool,
    build_graph: bool = False,
) -> dict:
    """
    Run one main research question against the property graph index.

    This function:
    - Creates a citation-based query engine.
    - Generates an answer with source citations.
    - Optionally builds a graph from retrieved triples.
    - Optionally aligns answer sentences with evidence.
    - Optionally calculates RAGAS scores.
    - Returns all data needed for saving, reporting, and evaluation.

    Args:
        index: The loaded LlamaIndex property graph index.
        raw_df: The original source dataframe, used to retrieve full Reddit posts.
        llm: The language model used for answering and evidence alignment.
        query: The main research question.
        top_k: Number of similar chunks to retrieve.
        chunk_sz: Citation chunk size used by the citation query engine.
        run_eval: Whether to calculate RAGAS scores.
        run_evidence_alignment: Whether to run evidence alignment.
        build_graph: Whether to build the knowledge graph visualisation.

    Returns:
        A dictionary containing the answer, sources, evidence rows, graph data,
        RAGAS scores, timestamps, and debugging information.
    """

    # Create a unique ID for this main query run.
    run_id = str(uuid.uuid4())

    # Create a citation query engine.
    # This retrieves relevant chunks and generates an answer with citations.
    citation_engine = CitationQueryEngine.from_args(
        index,
        llm=llm,
        similarity_top_k=top_k,
        citation_chunk_size=chunk_sz,
        text_qa_template=MAIN_QA_PROMPT,
    )

    # Record answer start time and start the timer.
    answer_started_at = iso_now()
    t0 = time.time()

    # Run the main query.
    response = citation_engine.query(query)

    # Record finish time and calculate duration.
    answer_finished_at = iso_now()
    answer_duration_seconds = round(time.time() - t0, 3)

    # Extract source nodes from the response.
    # If no source nodes exist, use an empty list.
    source_nodes = (
        list(response.source_nodes)
        if getattr(response, "source_nodes", None)
        else []
    )

    # Initialise graph-related outputs.
    retrieved_nodes = []
    query_triples = []
    triples = []
    trace_df = pd.DataFrame()
    graph_html = ""
    graph_build_source = "not_built"
    graph_empty_reason = "Graph building was skipped during batch run."

    # Build graph data only when requested.
    if build_graph:

        # First try to extract triples from citation engine source nodes.
        query_triples = get_triples_from_nodes(source_nodes)
        graph_build_source = "response.source_nodes"

        # If no triples were found in the source nodes, run a retriever fallback.
        if not query_triples:
            retriever = index.as_retriever(include_text=True)
            retrieved_nodes = retriever.retrieve(query)
            query_triples = get_triples_from_nodes(retrieved_nodes)
            graph_build_source = "retriever.retrieve"

        # Remove duplicate triples while keeping their original order.
        triples = list(dict.fromkeys(query_triples))

        # Track why the graph may be empty.
        graph_empty_reason = ""

        if not source_nodes:
            graph_empty_reason = "Citation engine returned no source nodes."
        elif not triples:
            graph_empty_reason = "No triples could be parsed from source/retrieved nodes."

        # Trace each unique triple back to the original source text.
        all_trace = []
        for s, r, o in set(triples):
            all_trace.extend(trace_triple_to_source(index, s, r, o))

        # Convert trace records into a dataframe if trace data exists.
        trace_df = (
            pd.DataFrame(all_trace)[
                [
                    "reddit_id",
                    "subject",
                    "relation",
                    "object",
                    "triple",
                    "matched_sentences",
                    "text_cleaned",
                ]
            ]
            if all_trace
            else pd.DataFrame()
        )

    # Build graph HTML if triples were found.
    graph_html = build_graph_html(triples, trace_df) if triples else ""

    # Store graph debugging information for later reporting.
    graph_debug = {
        "build_graph": build_graph,
        "num_source_nodes": len(source_nodes),
        "num_retrieved_nodes": len(retrieved_nodes),
        "num_query_triples": len(query_triples),
        "num_graph_triples": len(triples),
        "graph_empty": not bool(triples),
        "graph_build_source": graph_build_source,
        "graph_empty_reason": graph_empty_reason,
    }

    # Optionally align each cited answer sentence with supporting evidence.
    evidence_results = (
        align_evidence_for_response(llm, response.response, source_nodes)
        if run_evidence_alignment
        else []
    )

    # Extract citation numbers that were actually used in the answer.
    used = get_used_citations(response.response)

    # Store export-ready rows for cited chunks.
    export_rows = []

    # Process each retrieved source node.
    for i, node in enumerate(source_nodes):

        # Citation IDs are 1-based, while Python indexes are 0-based.
        cid = i + 1

        # Only export chunks that were actually cited in the answer.
        if cid not in used:
            continue

        # Extract the Reddit ID from node metadata.
        reddit_id = str(node.metadata.get("reddit_id", "N/A")).strip()

        # Look up the full Reddit post in the original dataframe.
        df_row = raw_df[raw_df["reddit_id"] == reddit_id]
        full_post = (
            df_row["text_cleaned"].values[0]
            if not df_row.empty
            else "Not found"
        )

        # Extract and clean the cited chunk text.
        raw_text = node.node.text if hasattr(node, "node") else node.text
        clean_chunk = strip_kg_triples(raw_text)

        # Find evidence-alignment results linked to this citation.
        chunk_ev = [
            e
            for e in evidence_results
            if cid in e["citations"]
        ]

        # Add one export row for this cited chunk.
        export_rows.append(
            {
                "run_id": run_id,
                "answer_started_at": answer_started_at,
                "answer_finished_at": answer_finished_at,
                "answer_duration_seconds": answer_duration_seconds,
                "citation": cid,
                "reddit_id": reddit_id,
                "score": round(node.score or 0.0, 3),
                "chunk": clean_chunk,
                "full_post": full_post,
                "query": query,
                "answer": response.response,
                "evidence": "\n\n".join(e["evidence"] for e in chunk_ev),
            }
        )

    # Store RAGAS scores.
    # None means evaluation was not requested.
    metric_scores = None

    # Run RAGAS evaluation if requested.
    if run_eval:

        # Use source nodes for evaluation.
        # If source nodes are unavailable, use retrieved nodes from graph fallback.
        context_nodes_for_eval = source_nodes or retrieved_nodes

        # Prepare shorter context chunks for RAGAS.
        retrieved_contexts = prepare_ragas_contexts(
            context_nodes_for_eval,
            max_contexts=3,
            max_chars_per_context=1500,
        )

        try:
            # Run the asynchronous RAGAS scoring function.
            raw_scores = asyncio.run(
                scoring_metric(query, retrieved_contexts, response.response)
            )

            # Convert scores to floats and keep None if a score is missing.
            metric_scores = {
                "Answer Relevancy": (
                    float(raw_scores.get("Answer Relevancy"))
                    if raw_scores.get("Answer Relevancy") is not None
                    else None
                ),
                "Faithfulness": (
                    float(raw_scores.get("Faithfulness"))
                    if raw_scores.get("Faithfulness") is not None
                    else None
                ),
                "Context Relevance": (
                    float(raw_scores.get("Context Relevance"))
                    if raw_scores.get("Context Relevance") is not None
                    else None
                ),
                "Response Groundedness": (
                    float(raw_scores.get("Response Groundedness"))
                    if raw_scores.get("Response Groundedness") is not None
                    else None
                ),
            }

        except Exception as e:
            # If RAGAS scoring fails, print the error and return empty scores.
            print(f"Metric scoring failed for main query: {e}")

            metric_scores = {
                "Answer Relevancy": None,
                "Faithfulness": None,
                "Context Relevance": None,
                "Response Groundedness": None,
            }

    # Return all outputs from the main query run.
    return {
        "run_id": run_id,
        "query": query,
        "response_obj": response,
        "response_text": response.response,
        "triples": triples,
        "trace_df": trace_df,
        "graph_html": graph_html,
        "evidence_results": evidence_results,
        "export_rows": export_rows,
        "metric_scores": metric_scores,
        "answer_started_at": answer_started_at,
        "answer_finished_at": answer_finished_at,
        "answer_duration_seconds": answer_duration_seconds,
        "graph_debug": graph_debug,
    }


def run_followup_query(
    index,
    llm,
    raw_df: pd.DataFrame,
    main_result: dict,
    followup_query: str,
    top_k: int,
    run_eval: bool,
) -> dict:
    """
    Run one follow-up question using the main answer and retrieved context.

    This function:
    - Retrieves new chunks for the follow-up query.
    - Keeps cited chunks from the main answer as priority context.
    - Generates a follow-up answer with C-style citations, such as [C1].
    - Builds context rows for export.
    - Optionally calculates RAGAS scores for the follow-up answer.

    Args:
        index: The loaded LlamaIndex property graph index.
        llm: The language model used to answer the follow-up question.
        raw_df: The original source dataframe, used to retrieve full Reddit posts.
        main_result: The output dictionary from run_main_query.
        followup_query: The follow-up question text.
        top_k: Number of similar chunks to retrieve.
        run_eval: Whether to calculate RAGAS scores.

    Returns:
        A dictionary containing the follow-up answer, context rows,
        context nodes, RAGAS scores, timestamps, and run IDs.
    """

    # Create a unique ID for this follow-up run.
    followup_run_id = str(uuid.uuid4())

    # Get the original main response object.
    main_response = main_result["response_obj"]

    # Create a retriever for the follow-up question.
    retriever = index.as_retriever(
        similarity_top_k=top_k,
        include_text=True,
    )

    # Retrieve new context nodes for the follow-up query.
    retrieved_nodes = retriever.retrieve(followup_query)

    # Find which citations were used in the main answer.
    used_ids = get_used_citations(main_response.response)

    # Keep only the main source nodes that were cited in the main answer.
    main_cited_nodes = [
        node
        for i, node in enumerate(main_response.source_nodes)
        if (i + 1) in used_ids
    ]

    # Use main cited chunks first, then add newly retrieved chunks.
    # This helps the follow-up answer stay connected to the main answer.
    followup_context_nodes = main_cited_nodes + [
        node
        for node in retrieved_nodes
        if node not in main_cited_nodes
    ]

    # Safety fallback:
    # If no follow-up context was found, reuse all main response source nodes.
    if not followup_context_nodes:
        followup_context_nodes = list(main_response.source_nodes)

    # Record answer start time and start the timer.
    started_at = iso_now()
    t0 = time.time()

    # Generate the follow-up answer using citation-labelled context chunks.
    sub_answer = ask_followup_with_citation(
        llm,
        followup_context_nodes,
        followup_query,
    )

    # Record finish time and calculate duration.
    finished_at = iso_now()
    duration_seconds = round(time.time() - t0, 3)

    # Extract C-style citations used in the follow-up answer, such as C1 and C2.
    subquery_used_raw = get_used_subquery_citations(sub_answer)

    # Store context rows for export and evaluation.
    subquery_rows = []

    # Process each context node used for the follow-up answer.
    for i, node in enumerate(followup_context_nodes):

        # Create a C-style context ID, such as C1, C2, C3.
        cid = f"C{i + 1}"

        # Extract and clean the context chunk.
        raw_text = node.node.text if hasattr(node, "node") else node.text
        clean = strip_kg_triples(raw_text)

        # Extract Reddit ID from node metadata.
        reddit_id = str(node.metadata.get("reddit_id", "N/A")).strip()

        # Retrieve the full Reddit post from the original dataframe.
        df_row = raw_df[raw_df["reddit_id"] == reddit_id]
        full_post = (
            df_row["text_cleaned"].values[0]
            if not df_row.empty
            else "Not found"
        )

        # Add one row for this follow-up context chunk.
        subquery_rows.append(
            {
                "followup_run_id": followup_run_id,
                "main_run_id": main_result["run_id"],
                "answer_started_at": started_at,
                "answer_finished_at": finished_at,
                "answer_duration_seconds": duration_seconds,
                "context_id": cid,
                "cited_in_answer": cid in subquery_used_raw,
                "reddit_id": reddit_id,
                "score": round(node.score or 0.0, 3),
                "chunk": clean,
                "full_post": full_post,
                "main_query": main_result["query"],
                "main_answer": main_result["response_text"],
                "followup_query": followup_query,
                "followup_answer": sub_answer,
            }
        )

    # Store RAGAS scores.
    # None means evaluation was not requested.
    metric_scores = None

    # Run RAGAS evaluation if requested.
    if run_eval:

        # Prepare more context for follow-up evaluation.
        # Follow-ups may need both main cited chunks and newly retrieved chunks.
        retrieved_contexts = prepare_ragas_contexts(
            followup_context_nodes,
            max_contexts=5,
            max_chars_per_context=2500,
        )

        try:
            # Run the asynchronous RAGAS scoring function.
            raw_scores = asyncio.run(
                scoring_metric(followup_query, retrieved_contexts, sub_answer)
            )

            # Convert scores to floats and keep None if a score is missing.
            metric_scores = {
                "Answer Relevancy": (
                    float(raw_scores.get("Answer Relevancy"))
                    if raw_scores.get("Answer Relevancy") is not None
                    else None
                ),
                "Faithfulness": (
                    float(raw_scores.get("Faithfulness"))
                    if raw_scores.get("Faithfulness") is not None
                    else None
                ),
                "Context Relevance": (
                    float(raw_scores.get("Context Relevance"))
                    if raw_scores.get("Context Relevance") is not None
                    else None
                ),
                "Response Groundedness": (
                    float(raw_scores.get("Response Groundedness"))
                    if raw_scores.get("Response Groundedness") is not None
                    else None
                ),
            }

        except Exception as e:
            # If RAGAS scoring fails, print the error and return empty scores.
            print(f"Metric scoring failed for follow-up query: {e}")

            metric_scores = {
                "Answer Relevancy": None,
                "Faithfulness": None,
                "Context Relevance": None,
                "Response Groundedness": None,
            }

    # Return all outputs from the follow-up query run.
    return {
        "followup_run_id": followup_run_id,
        "main_run_id": main_result["run_id"],
        "followup_query": followup_query,
        "followup_answer": sub_answer,
        "context_nodes": followup_context_nodes,
        "context_rows": subquery_rows,
        "metric_scores": metric_scores,
        "answer_started_at": started_at,
        "answer_finished_at": finished_at,
        "answer_duration_seconds": duration_seconds,
    }