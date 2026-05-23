# Import dataclass to create simple structured data containers.
# Import field for possible default values or default factories.
# Note: field is imported here but is not currently used in this code.
from dataclasses import dataclass, field

# Import Optional for values that can be None.
# Import Any for values where the exact type may vary, such as a LlamaIndex response object.
from typing import Optional, Any

# Import pandas because some result objects store outputs as pandas DataFrames.
import pandas as pd


@dataclass
class GraphDebug:
    """
    Store diagnostic information about graph construction.

    This class helps track:
    - how many nodes were used,
    - how many triples were found,
    - whether the graph is empty,
    - where the graph data came from,
    - why a graph could not be built.
    """

    # Number of source nodes returned by the citation query engine.
    num_source_nodes: int = 0

    # Number of nodes retrieved by a fallback retriever, if used.
    num_retrieved_nodes: int = 0

    # Number of triples parsed from the retrieved or source nodes.
    num_query_triples: int = 0

    # Number of unique triples used to build the final graph.
    num_graph_triples: int = 0

    # Indicates whether the final graph has no triples.
    graph_empty: bool = False

    # Records where the graph triples came from.
    # Example values may include "response.source_nodes" or "retriever.retrieve".
    graph_build_source: str = ""

    # Stores the reason why the graph is empty, if no graph could be built.
    graph_empty_reason: str = ""


@dataclass
class MainQueryResult:
    """
    Store all outputs from one main research question query.

    This class groups together the generated answer, retrieved evidence,
    graph data, evaluation scores, timing information, and debug details.
    """

    # Unique ID for the main query run.
    run_id: str

    # The main research question asked by the user.
    query: str

    # The original response object returned by the query engine.
    # This may contain source nodes, metadata, and the generated response.
    response_obj: Any

    # The generated answer text.
    response_text: str

    # Knowledge graph triples extracted from the retrieved source nodes.
    # Each triple is usually in the form: (subject, relation, object).
    triples: list[tuple]

    # DataFrame containing trace information that links triples back to source text.
    trace_df: pd.DataFrame

    # HTML string for the generated knowledge graph visualisation.
    graph_html: str

    # Sentence-level evidence alignment results.
    evidence_results: list[dict]

    # Rows prepared for export, such as cited chunks, full posts, and evidence.
    export_rows: list[dict]

    # RAGAS or other evaluation metric scores.
    # This can be None if evaluation was not run.
    metric_scores: Optional[dict]

    # Timestamp showing when answer generation started.
    answer_started_at: str

    # Timestamp showing when answer generation finished.
    answer_finished_at: str

    # Total time taken to generate the answer, in seconds.
    answer_duration_seconds: float

    # Graph diagnostic information for this main query.
    graph_debug: GraphDebug


@dataclass
class FollowupQueryResult:
    """
    Store all outputs from one follow-up question query.

    This class keeps the follow-up answer, context used for the answer,
    evaluation scores, timing information, and links back to the main query.
    """

    # Unique ID for the follow-up query run.
    followup_run_id: str

    # ID of the main query run linked to this follow-up.
    main_run_id: str

    # The follow-up question asked after the main research question.
    followup_query: str

    # The generated answer for the follow-up question.
    followup_answer: str

    # Source or context nodes used to answer the follow-up question.
    context_nodes: list

    # Export-ready rows describing the context chunks used in the follow-up answer.
    context_rows: list[dict]

    # RAGAS or other evaluation metric scores.
    # This can be None if evaluation was not run.
    metric_scores: Optional[dict]

    # Timestamp showing when follow-up answer generation started.
    answer_started_at: str

    # Timestamp showing when follow-up answer generation finished.
    answer_finished_at: str

    # Total time taken to generate the follow-up answer, in seconds.
    answer_duration_seconds: float