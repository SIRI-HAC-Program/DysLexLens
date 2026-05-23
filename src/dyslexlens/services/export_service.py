# services/export_service.py

# Import json to save run information and batch metadata as JSON files.
import json

# Import shutil to copy graph PNG files into the shared graph gallery folder.
import shutil

# Import Path for safe and readable file path handling.
from pathlib import Path

# Import Optional for type hints where a parameter can be None.
from typing import Optional

# Import pandas for creating and saving CSV files.
import pandas as pd

# Import shared project configuration values.
from config import (
    COMBINED_DIR,
    FIXED_INDEX_LLM_MODEL,
    FIXED_EMBED_MODEL,
)

# Import helper function used to convert graph HTML into a PNG screenshot.
from services.graph_service import save_graph_screenshot_from_html

# Import file utility functions for CSV appending and safe file naming.
from utils.file_utils import (
    append_rows_to_csv,
    safe_file_stem,
)

# Import text utility functions for citation parsing and chunk cleaning.
from utils.text_utils import (
    parse_sentence_citations,
    parse_subquery_sentence_citations,
    strip_kg_triples,
)


def build_main_evaluator_rows(
    batch_id: str,
    question_id: str,
    query_llm_model: str,
    query: str,
    response_text: str,
    raw_df: pd.DataFrame,
    source_nodes: list,
    evidence_results: list[dict],
    main_run_id: str,
    answer_started_at: str,
    answer_finished_at: str,
    answer_duration_seconds: float,
    metric_scores: Optional[dict] = None,
) -> list[dict]:
    """
    Build evaluator-ready rows for a main research question response.

    Each generated answer is split into sentence-level claim candidates.
    Each claim is then linked to its citation, source chunk, Reddit ID,
    full Reddit post, evidence alignment block, and RAGAS scores.

    These rows are later used for human evaluation and qualitative review.
    """

    # Store all evaluator rows for the current main question.
    rows = []

    # Use an empty dictionary if metric scores are not available.
    metric_scores = metric_scores or {}

    # Parse the response into sentences and extract citation IDs from each sentence.
    sentence_items = parse_sentence_citations(response_text or "")

    # Process each sentence-level claim candidate.
    for sentence_idx, item in enumerate(sentence_items, start=1):
        claim_candidate = item["sentence"]
        citation_ids = item["citations"]

        # If a sentence has no citation, still create an evaluator row.
        # This helps human reviewers identify unsupported or uncited claims.
        if not citation_ids:
            rows.append(
                {
                    "batch_id": batch_id,
                    "question_id": question_id,
                    "main_run_id": main_run_id,
                    "sentence_id": sentence_idx,
                    "answer_started_at": answer_started_at,
                    "answer_finished_at": answer_finished_at,
                    "answer_duration_seconds": answer_duration_seconds,
                    "query_llm_model": query_llm_model,
                    "fixed_index_llm_model": FIXED_INDEX_LLM_MODEL,
                    "fixed_embed_model": FIXED_EMBED_MODEL,
                    "query": query,
                    "full_answer": response_text,
                    "Answer Relevancy": metric_scores.get("Answer Relevancy"),
                    "Faithfulness": metric_scores.get("Faithfulness"),
                    "Context Relevance": metric_scores.get("Context Relevance"),
                    "Response Groundedness": metric_scores.get("Response Groundedness"),
                    "claim_candidate": claim_candidate,
                    "citation_id": None,
                    "reddit_id": None,
                    "retrieval_score": None,
                    "verbatim_evidence": "No citation.",
                    "evidence_alignment_block": "",
                    "source_chunk": "",
                    "full_post": "",
                    "atomic_claim_after_human_decomposition": "",
                    "accuracy_present_in_original_source": "",
                    "support_strength_1_to_3": "",
                    "interpretative_utility_yes_no_or_comment": "",
                    "reviewer_notes": "",
                }
            )
            continue

        # Create one evaluator row for each citation used in the sentence.
        for cid in citation_ids:
            # Citation IDs are 1-based, while Python lists are 0-based.
            # Skip the citation if it does not match an available source node.
            if not (0 <= cid - 1 < len(source_nodes)):
                continue

            # Get the source node linked to this citation.
            node = source_nodes[cid - 1]

            # Extract the Reddit ID from the node metadata.
            reddit_id = str(node.metadata.get("reddit_id", "N/A")).strip()

            # Store the retrieval score rounded to three decimal places.
            retrieval_score = round(node.score or 0.0, 3)

            # LlamaIndex nodes may store text in node.node.text or node.text.
            raw_text = node.node.text if hasattr(node, "node") else node.text

            # Remove knowledge graph triples so the chunk is easier to review.
            clean_chunk = strip_kg_triples(raw_text)

            # Look up the full Reddit post using reddit_id from the raw dataframe.
            df_row = raw_df[raw_df["reddit_id"] == reddit_id]
            full_post = df_row["text_cleaned"].values[0] if not df_row.empty else "Not found"

            # Find evidence-alignment outputs that are linked to the same citation.
            aligned_blocks = [
                e["evidence"]
                for e in evidence_results
                if cid in e.get("citations", [])
            ]

            # Combine all matching evidence alignment blocks into one text field.
            evidence_alignment_block = "\n\n".join(aligned_blocks).strip()

            # Extract short verbatim evidence phrases from the evidence alignment text.
            # This expects lines in a format such as "Evidence: quoted phrase".
            verbatim_match = []
            for line in evidence_alignment_block.splitlines():
                if "Evidence" in line and ":" in line:
                    verbatim_match.append(line.split(":", 1)[1].strip())

            # Join all extracted evidence phrases into one field.
            verbatim_evidence = " | ".join(verbatim_match) if verbatim_match else ""

            # Add the completed evaluator row.
            rows.append(
                {
                    "batch_id": batch_id,
                    "question_id": question_id,
                    "main_run_id": main_run_id,
                    "sentence_id": sentence_idx,
                    "answer_started_at": answer_started_at,
                    "answer_finished_at": answer_finished_at,
                    "answer_duration_seconds": answer_duration_seconds,
                    "query_llm_model": query_llm_model,
                    "fixed_index_llm_model": FIXED_INDEX_LLM_MODEL,
                    "fixed_embed_model": FIXED_EMBED_MODEL,
                    "query": query,
                    "full_answer": response_text,
                    "Answer Relevancy": metric_scores.get("Answer Relevancy"),
                    "Faithfulness": metric_scores.get("Faithfulness"),
                    "Context Relevance": metric_scores.get("Context Relevance"),
                    "Response Groundedness": metric_scores.get("Response Groundedness"),
                    "claim_candidate": claim_candidate,
                    "citation_id": cid,
                    "reddit_id": reddit_id,
                    "retrieval_score": retrieval_score,
                    "verbatim_evidence": verbatim_evidence,
                    "evidence_alignment_block": evidence_alignment_block,
                    "source_chunk": clean_chunk,
                    "full_post": full_post,
                    "atomic_claim_after_human_decomposition": "",
                    "accuracy_present_in_original_source": "",
                    "support_strength_1_to_3": "",
                    "interpretative_utility_yes_no_or_comment": "",
                    "reviewer_notes": "",
                }
            )

    # Return all evaluator-ready rows for the main answer.
    return rows


def build_followup_evaluator_rows(
    batch_id: str,
    question_id: str,
    query_llm_model: str,
    main_query: str,
    main_answer: str,
    followup_query: str,
    followup_answer: str,
    raw_df: pd.DataFrame,
    context_nodes: list,
    followup_run_id: str,
    main_run_id: str,
    answer_started_at: str,
    answer_finished_at: str,
    answer_duration_seconds: float,
    metric_scores: Optional[dict] = None,
) -> list[dict]:
    """
    Build evaluator-ready rows for a follow-up response.

    Follow-up responses use citation labels such as C1, C2, and C3.
    This function maps those labels back to the context nodes used
    to answer the follow-up question.
    """

    # Store all evaluator rows for the current follow-up answer.
    rows = []

    # Use an empty dictionary if metric scores are not available.
    metric_scores = metric_scores or {}

    # Parse the follow-up answer into sentence-level claims and C-style citations.
    sentence_items = parse_subquery_sentence_citations(followup_answer or "")

    # Process each sentence-level claim candidate.
    for sentence_idx, item in enumerate(sentence_items, start=1):
        claim_candidate = item["sentence"]
        citation_ids = item["citations"]

        # If a sentence has no citation, create a row with empty provenance fields.
        if not citation_ids:
            rows.append(
                {
                    "batch_id": batch_id,
                    "question_id": question_id,
                    "main_run_id": main_run_id,
                    "followup_run_id": followup_run_id,
                    "sentence_id": sentence_idx,
                    "answer_started_at": answer_started_at,
                    "answer_finished_at": answer_finished_at,
                    "answer_duration_seconds": answer_duration_seconds,
                    "query_llm_model": query_llm_model,
                    "fixed_index_llm_model": FIXED_INDEX_LLM_MODEL,
                    "fixed_embed_model": FIXED_EMBED_MODEL,
                    "main_query": main_query,
                    "main_answer": main_answer,
                    "followup_query": followup_query,
                    "followup_answer": followup_answer,
                    "Answer Relevancy": metric_scores.get("Answer Relevancy"),
                    "Faithfulness": metric_scores.get("Faithfulness"),
                    "Context Relevance": metric_scores.get("Context Relevance"),
                    "Response Groundedness": metric_scores.get("Response Groundedness"),
                    "claim_candidate": claim_candidate,
                    "citation_id": None,
                    "reddit_id": None,
                    "retrieval_score": None,
                    "verbatim_evidence": "No citation.",
                    "source_chunk": "",
                    "full_post": "",
                    "atomic_claim_after_human_decomposition": "",
                    "accuracy_present_in_original_source": "",
                    "support_strength_1_to_3": "",
                    "interpretative_utility_yes_no_or_comment": "",
                    "reviewer_notes": "",
                }
            )
            continue

        # Create one evaluator row for each follow-up citation.
        for cid in citation_ids:
            # Convert C-style citation IDs such as C1 into a zero-based list index.
            idx = int(cid[1:]) - 1

            # Skip the citation if it does not match an available context node.
            if not (0 <= idx < len(context_nodes)):
                continue

            # Get the context node linked to the follow-up citation.
            node = context_nodes[idx]

            # Extract source metadata and retrieval score.
            reddit_id = str(node.metadata.get("reddit_id", "N/A")).strip()
            retrieval_score = round(node.score or 0.0, 3)

            # LlamaIndex nodes may store text in node.node.text or node.text.
            raw_text = node.node.text if hasattr(node, "node") else node.text

            # Clean the chunk by removing knowledge graph triples.
            clean_chunk = strip_kg_triples(raw_text)

            # Retrieve the full Reddit post from the original source dataframe.
            df_row = raw_df[raw_df["reddit_id"] == reddit_id]
            full_post = df_row["text_cleaned"].values[0] if not df_row.empty else "Not found"

            # Add the completed evaluator row for this cited follow-up claim.
            rows.append(
                {
                    "batch_id": batch_id,
                    "question_id": question_id,
                    "main_run_id": main_run_id,
                    "followup_run_id": followup_run_id,
                    "sentence_id": sentence_idx,
                    "answer_started_at": answer_started_at,
                    "answer_finished_at": answer_finished_at,
                    "answer_duration_seconds": answer_duration_seconds,
                    "query_llm_model": query_llm_model,
                    "fixed_index_llm_model": FIXED_INDEX_LLM_MODEL,
                    "fixed_embed_model": FIXED_EMBED_MODEL,
                    "main_query": main_query,
                    "main_answer": main_answer,
                    "followup_query": followup_query,
                    "followup_answer": followup_answer,
                    "Answer Relevancy": metric_scores.get("Answer Relevancy"),
                    "Faithfulness": metric_scores.get("Faithfulness"),
                    "Context Relevance": metric_scores.get("Context Relevance"),
                    "Response Groundedness": metric_scores.get("Response Groundedness"),
                    "claim_candidate": claim_candidate,
                    "citation_id": cid,
                    "reddit_id": reddit_id,
                    "retrieval_score": retrieval_score,
                    "verbatim_evidence": clean_chunk,
                    "source_chunk": clean_chunk,
                    "full_post": full_post,
                    "atomic_claim_after_human_decomposition": "",
                    "accuracy_present_in_original_source": "",
                    "support_strength_1_to_3": "",
                    "interpretative_utility_yes_no_or_comment": "",
                    "reviewer_notes": "",
                }
            )

    # Return all evaluator-ready rows for the follow-up answer.
    return rows


def save_single_main_run(
    question_dir: Path,
    main_result: dict,
    graph_gallery_dir: Optional[Path] = None,
    gallery_file_stem: Optional[str] = None,
    save_graph_png: bool = False,
) -> dict:
    """
    Save all files for a single main research question run.

    This includes:
    - the generated answer,
    - the graph HTML,
    - optional graph PNG screenshot,
    - evidence report,
    - extracted triples,
    - RAGAS metrics,
    - triple trace file,
    - run metadata JSON.
    """

    # Create the output folder for this question if it does not already exist.
    question_dir.mkdir(parents=True, exist_ok=True)

    # Define file paths for the main answer and graph outputs.
    answer_path = question_dir / "answer.txt"
    graph_html_path = question_dir / "graph.html"
    graph_png_path = question_dir / "graph.png"

    # Track the graph screenshot status for reporting and debugging.
    screenshot_status = "Not attempted"

    # Save the generated answer as a text file.
    answer_path.write_text(main_result["response_text"] or "", encoding="utf-8")

    # Save the generated graph HTML, even if it is empty.
    graph_html_path.write_text(main_result["graph_html"] or "", encoding="utf-8")

    # Save the evidence report if evidence rows are available.
    if main_result["export_rows"]:
        pd.DataFrame(main_result["export_rows"]).to_csv(
            question_dir / "evidence_report.csv",
            index=False,
        )

    # Save extracted knowledge graph triples if available.
    if main_result["triples"]:
        pd.DataFrame(
            main_result["triples"],
            columns=["subject", "relation", "object"],
        ).to_csv(question_dir / "triples.csv", index=False)

    # Save RAGAS metric scores if evaluation was run.
    if main_result["metric_scores"]:
        pd.DataFrame([main_result["metric_scores"]]).to_csv(
            question_dir / "metrics.csv",
            index=False,
        )

    # Save the triple trace dataframe if it contains rows.
    if not main_result["trace_df"].empty:
        main_result["trace_df"].to_csv(
            question_dir / "triple_trace.csv",
            index=False,
        )

    # Optionally create a PNG screenshot from the graph HTML.
    if save_graph_png and main_result["graph_html"]:
        err = save_graph_screenshot_from_html(
            main_result["graph_html"],
            graph_png_path,
        )

        # If screenshot creation worked, update the status and copy it to the gallery.
        if err is None:
            screenshot_status = "Saved"

            # Save a duplicate copy in the graph gallery folder if provided.
            if graph_gallery_dir is not None:
                graph_gallery_dir.mkdir(parents=True, exist_ok=True)
                gallery_name = f"{gallery_file_stem or 'graph'}.png"
                shutil.copyfile(graph_png_path, graph_gallery_dir / gallery_name)

        # If screenshot creation failed, store the error message.
        else:
            screenshot_status = err

    # Save run-level metadata for this main question.
    with open(question_dir / "main_run_info.json", "w", encoding="utf-8") as f:
        json.dump(
            {
                "main_run_id": main_result["run_id"],
                "query": main_result["query"],
                "answer_started_at": main_result["answer_started_at"],
                "answer_finished_at": main_result["answer_finished_at"],
                "answer_duration_seconds": main_result["answer_duration_seconds"],
                "graph_html_file": str(graph_html_path),
                "graph_png_file": str(graph_png_path) if graph_png_path.exists() else None,
                "graph_screenshot_status": screenshot_status,
                "graph_debug": main_result.get("graph_debug"),
            },
            f,
            indent=2,
        )

    # Return key saved file paths so other services or UI components can use them.
    return {
        "answer_file": str(answer_path),
        "graph_file": str(graph_html_path),
        "graph_png_file": str(graph_png_path) if graph_png_path.exists() else None,
        "graph_screenshot_status": screenshot_status,
    }


def save_single_followup_runs(question_dir: Path, followup_results: list[dict]):
    """
    Save all follow-up outputs for a single main research question.

    Each follow-up gets its own folder containing:
    - follow-up answer,
    - retrieved context report,
    - optional RAGAS metrics,
    - follow-up run metadata.

    The function also saves summary CSV files for all follow-ups under the question folder.
    """

    # Create a followups folder inside the current question folder.
    followup_dir = question_dir / "followups"
    followup_dir.mkdir(parents=True, exist_ok=True)

    # Store all follow-up summary rows and context rows.
    followup_summary_rows = []
    followup_context_rows = []

    # Save each follow-up result in a separate folder.
    for idx, fr in enumerate(followup_results, start=1):
        # Create a safe folder name using the follow-up number and query text.
        stem = f"{idx:02d}__{safe_file_stem(fr['followup_query'])}"
        item_dir = followup_dir / stem
        item_dir.mkdir(parents=True, exist_ok=True)

        # Save the follow-up answer as a text file.
        (item_dir / "followup_answer.txt").write_text(
            fr["followup_answer"] or "",
            encoding="utf-8",
        )

        # Save the retrieved context rows used to answer the follow-up.
        pd.DataFrame(fr["context_rows"]).to_csv(
            item_dir / "followup_context_report.csv",
            index=False,
        )

        # Save follow-up RAGAS scores if available.
        if fr.get("metric_scores"):
            pd.DataFrame([fr["metric_scores"]]).to_csv(
                item_dir / "followup_metrics.csv",
                index=False,
            )

        # Save follow-up run metadata as JSON.
        with open(item_dir / "followup_run_info.json", "w", encoding="utf-8") as f:
            json.dump(
                {
                    "followup_run_id": fr["followup_run_id"],
                    "main_run_id": fr["main_run_id"],
                    "followup_query": fr["followup_query"],
                    "answer_started_at": fr["answer_started_at"],
                    "answer_finished_at": fr["answer_finished_at"],
                    "answer_duration_seconds": fr["answer_duration_seconds"],
                    "metric_scores": fr.get("metric_scores"),
                },
                f,
                indent=2,
            )

        # Build a summary row for this follow-up.
        followup_summary_rows.append(
            {
                "followup_run_id": fr["followup_run_id"],
                "main_run_id": fr["main_run_id"],
                "followup_column": fr.get("followup_column"),
                "followup_number": fr.get("followup_number"),
                "followup_query": fr["followup_query"],
                "followup_answer": fr["followup_answer"],
                "answer_started_at": fr["answer_started_at"],
                "answer_finished_at": fr["answer_finished_at"],
                "answer_duration_seconds": fr["answer_duration_seconds"],
                "Answer Relevancy": (
                    fr["metric_scores"].get("Answer Relevancy")
                    if fr["metric_scores"]
                    else None
                ),
                "Faithfulness": (
                    fr["metric_scores"].get("Faithfulness")
                    if fr["metric_scores"]
                    else None
                ),
                "Context Relevance": (
                    fr["metric_scores"].get("Context Relevance")
                    if fr["metric_scores"]
                    else None
                ),
                "Response Groundedness": (
                    fr["metric_scores"].get("Response Groundedness")
                    if fr["metric_scores"]
                    else None
                ),
                "path": str(item_dir),
            }
        )

        # Add this follow-up's context rows to the combined context list.
        followup_context_rows.extend(fr["context_rows"])

    # Save a CSV containing all follow-up run summaries for this question.
    if followup_summary_rows:
        pd.DataFrame(followup_summary_rows).to_csv(
            question_dir / "followup_runs.csv",
            index=False,
        )

    # Save a CSV containing all follow-up context rows for this question.
    if followup_context_rows:
        pd.DataFrame(followup_context_rows).to_csv(
            question_dir / "followup_contexts.csv",
            index=False,
        )


def build_all_results_df(
    main_eval_df: pd.DataFrame,
    followup_eval_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Combine main-question and follow-up evaluator rows into one dataframe.

    The combined dataframe is useful for:
    - batch-level reporting,
    - human audit preparation,
    - qualitative review,
    - RAGAS summary analysis.
    """

    # Store non-empty dataframes before combining them.
    frames = []

    # Add main-question rows if available.
    if not main_eval_df.empty:
        main_df = main_eval_df.copy()

        # Mark these rows as main-question results.
        main_df.insert(0, "result_type", "main")

        # Add matching columns so main and follow-up rows have a shared structure.
        # The original main columns are kept unchanged.
        main_df["main_query"] = main_df["query"]
        main_df["main_answer"] = main_df["full_answer"]
        main_df["followup_column"] = None
        main_df["followup_number"] = None
        main_df["followup_run_id"] = None
        main_df["followup_query"] = None
        main_df["followup_answer"] = None

        frames.append(main_df)

    # Add follow-up rows if available.
    if not followup_eval_df.empty:
        followup_df = followup_eval_df.copy()

        # Mark these rows as follow-up results.
        followup_df.insert(0, "result_type", "followup")

        frames.append(followup_df)

    # Return an empty dataframe if there are no results to combine.
    if not frames:
        return pd.DataFrame()

    # Combine main and follow-up rows into one dataframe.
    all_results_df = pd.concat(
        frames,
        ignore_index=True,
        sort=False,
    )

    return all_results_df


def save_batch_outputs(
    batch_dir: Path,
    batch_manifest: dict,
    all_results_df: pd.DataFrame,
):
    """
    Save batch-level output files.

    This function:
    - saves the batch manifest JSON,
    - saves the combined all-results CSV inside the batch folder,
    - appends the same rows to the combined output directory.
    """

    # Create the batch output folder if it does not already exist.
    batch_dir.mkdir(parents=True, exist_ok=True)

    # Save the batch metadata as a JSON file.
    with open(batch_dir / "batch_manifest.json", "w", encoding="utf-8") as f:
        json.dump(batch_manifest, f, indent=2)

    # Get the model name and batch ID for output file naming.
    model_name = batch_manifest.get("query_llm_model", "unknown_model")
    batch_id = batch_manifest.get("batch_id", "unknown_batch")

    # Convert the model name into a safe file-name format.
    safe_model = safe_file_stem(model_name)

    # Build the output CSV filename.
    output_filename = f"all_results__{safe_model}__{batch_id}.csv"

    # Save the combined results inside the current batch folder.
    all_results_df.to_csv(
        batch_dir / output_filename,
        index=False,
    )

    # Also append the result rows to the combined directory if data exists.
    # This supports long-term collection of outputs across multiple batch runs.
    if not all_results_df.empty:
        append_rows_to_csv(
            COMBINED_DIR / output_filename,
            all_results_df.to_dict("records"),
        )