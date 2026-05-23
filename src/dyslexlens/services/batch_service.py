# services/batch_service.py

import uuid
from datetime import datetime
from pathlib import Path

import pandas as pd
import streamlit as st

from config import (
    FIXED_INDEX_LLM_MODEL,
    FIXED_EMBED_MODEL,
    GRAPH_SCREENSHOTS_DIRNAME,
)
from services.query_service import run_main_query, run_followup_query
from services.export_service import (
    build_main_evaluator_rows,
    build_followup_evaluator_rows,
    save_single_main_run,
    save_single_followup_runs,
    build_all_results_df,
    save_batch_outputs,
)
from utils.file_utils import safe_model_dir_name, safe_file_stem
from utils.text_utils import get_used_citations


def run_batch_questions(
    index,
    raw_df: pd.DataFrame,
    llm,
    question_df: pd.DataFrame,
    followup_cols: list[str],
    query_llm_model: str,
    top_k: int,
    chunk_sz: int,
    run_eval: bool,
    run_evidence_alignment: bool,
    build_graphs_during_batch: bool,
    save_graph_png: bool,
) -> dict:
    """
    Run all main research questions and their follow-up questions.

    This function:
    - Creates a unique batch folder.
    - Runs each main research question.
    - Runs follow-up questions linked to each main question.
    - Saves answers, evidence reports, graph files, metrics, and evaluator-ready CSVs.
    - Builds a combined results dataframe for later analysis.
    """

    # Create a unique ID for this batch run.
    batch_id = str(uuid.uuid4())

    # Create a readable timestamp for folder naming.
    batch_timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create the main folder where all batch outputs will be saved.
    batch_dir = (
        Path("saved_runs")
        / safe_model_dir_name(query_llm_model)
        / f"batch_{batch_timestamp}"
    )

    # Create a folder path for saved graph screenshots.
    graph_gallery_dir = batch_dir / GRAPH_SCREENSHOTS_DIRNAME

    # Store summary and detailed outputs for main questions.
    main_summary_rows = []
    main_evidence_rows = []
    main_evaluator_rows = []

    # Store summary and detailed outputs for follow-up questions.
    followup_summary_rows = []
    followup_context_rows = []
    followup_evaluator_rows = []

    # Convert the question dataframe into a list of dictionaries.
    question_records = question_df.to_dict("records")

    # Count the total number of tasks to show correct progress in Streamlit.
    total_steps = 0
    for rec in question_records:
        total_steps += 1  # One step for the main question.

        # Add one step for each non-empty follow-up question.
        total_steps += sum(
            1
            for col in followup_cols
            if pd.notna(rec.get(col)) and str(rec.get(col)).strip()
        )

    # Create Streamlit progress and status elements.
    progress = st.progress(0.0)
    status = st.empty()

    current_step = 0
    last_main_result = None
    main_results_by_question = []

    # Process each research question.
    for q_idx, rec in enumerate(question_records, start=1):
        # Use the question_id from the CSV if available.
        # Otherwise, create a default ID such as RQ1, RQ2, etc.
        question_id = str(rec.get("question_id", f"RQ{q_idx}"))

        # Read and clean the main research question text.
        main_query = str(rec.get("research_question", "")).strip()

        # Skip empty questions.
        if not main_query:
            continue

        status.info(
            f"Running main question {q_idx}/{len(question_records)}: {question_id}"
        )

        # Run the main query through the query service.
        try:
            main_result = run_main_query(
                index=index,
                raw_df=raw_df,
                llm=llm,
                query=main_query,
                top_k=top_k,
                chunk_sz=chunk_sz,
                run_eval=run_eval,
                run_evidence_alignment=run_evidence_alignment,
                build_graph=build_graphs_during_batch,
            )
        except Exception as e:
            status.error(f"Failed main question {question_id}: {e}")
            raise

        # Keep the most recent main result.
        last_main_result = main_result

        # Create a separate folder for this question.
        question_dir = batch_dir / f"{q_idx:02d}__{safe_file_stem(question_id)}"

        # Save files for the main question, such as answer, graph, metrics, and evidence.
        save_info = save_single_main_run(
            question_dir=question_dir,
            main_result=main_result,
            graph_gallery_dir=graph_gallery_dir,
            gallery_file_stem=f"{q_idx:02d}__{safe_file_stem(question_id)}",
            save_graph_png=save_graph_png,
        )

        # Keep metadata so the UI can later show graphs and question details.
        main_results_by_question.append(
            {
                "question_index": q_idx,
                "question_id": question_id,
                "query": main_query,
                "main_result": main_result,
                "question_dir": str(question_dir),
                "graph_file": save_info.get("graph_file"),
                "graph_png_file": save_info.get("graph_png_file"),
                "graph_screenshot_status": save_info.get("graph_screenshot_status"),
            }
        )

        # Read graph debug information if it exists.
        gdbg = main_result.get("graph_debug", {})

        # Add one summary row for this main question.
        main_summary_rows.append(
            {
                "batch_id": batch_id,
                "question_id": question_id,
                "main_run_id": main_result["run_id"],
                "query_llm_model": query_llm_model,
                "fixed_index_llm_model": FIXED_INDEX_LLM_MODEL,
                "fixed_embed_model": FIXED_EMBED_MODEL,
                "query": main_query,
                "answer": main_result["response_text"],
                "answer_started_at": main_result["answer_started_at"],
                "answer_finished_at": main_result["answer_finished_at"],
                "answer_duration_seconds": main_result["answer_duration_seconds"],
                "num_citations_used": len(
                    get_used_citations(main_result["response_text"])
                ),
                "num_triples": len(main_result["triples"]),
                "num_export_rows": len(main_result["export_rows"]),
                "Answer Relevancy": (
                    main_result["metric_scores"].get("Answer Relevancy")
                    if main_result["metric_scores"]
                    else None
                ),
                "Faithfulness": (
                    main_result["metric_scores"].get("Faithfulness")
                    if main_result["metric_scores"]
                    else None
                ),
                "Context Relevance": (
                    main_result["metric_scores"].get("Context Relevance")
                    if main_result["metric_scores"]
                    else None
                ),
                "Response Groundedness": (
                    main_result["metric_scores"].get("Response Groundedness")
                    if main_result["metric_scores"]
                    else None
                ),
                "question_dir": str(question_dir),
                "answer_file": save_info.get("answer_file"),
                "graph_file": save_info.get("graph_file"),
                "graph_png_file": save_info.get("graph_png_file"),
                "graph_screenshot_status": save_info.get("graph_screenshot_status"),
                "evidence_report_file": str(question_dir / "evidence_report.csv"),
                "triples_file": str(question_dir / "triples.csv"),
                "metrics_file": str(question_dir / "metrics.csv"),
                "trace_file": str(question_dir / "triple_trace.csv"),
                "num_source_nodes": gdbg.get("num_source_nodes"),
                "num_retrieved_nodes": gdbg.get("num_retrieved_nodes"),
                "num_query_triples": gdbg.get("num_query_triples"),
                "num_graph_triples": gdbg.get("num_graph_triples"),
                "graph_empty": gdbg.get("graph_empty"),
                "graph_build_source": gdbg.get("graph_build_source"),
                "graph_empty_reason": gdbg.get("graph_empty_reason"),
            }
        )

        # Add evidence rows for this main question.
        main_evidence_rows.extend(
            [
                {"batch_id": batch_id, "question_id": question_id, **row}
                for row in main_result["export_rows"]
            ]
        )

        # Build evaluator-ready rows for human assessment.
        main_evaluator_rows.extend(
            build_main_evaluator_rows(
                batch_id=batch_id,
                question_id=question_id,
                query_llm_model=query_llm_model,
                query=main_query,
                response_text=main_result["response_text"],
                metric_scores=main_result["metric_scores"],
                raw_df=raw_df,
                source_nodes=main_result["response_obj"].source_nodes,
                evidence_results=main_result["evidence_results"],
                main_run_id=main_result["run_id"],
                answer_started_at=main_result["answer_started_at"],
                answer_finished_at=main_result["answer_finished_at"],
                answer_duration_seconds=main_result["answer_duration_seconds"],
            )
        )

        # Update progress after completing the main question.
        current_step += 1
        progress.progress(min(current_step / max(total_steps, 1), 1.0))

        # Store all follow-up results for the current main question.
        followup_results = []

        # Process each follow-up column.
        for followup_col in followup_cols:
            followup_query = rec.get(followup_col)

            # Skip empty follow-up questions.
            if pd.isna(followup_query) or not str(followup_query).strip():
                continue

            followup_query = str(followup_query).strip()
            status.info(f"Running follow-up for {question_id}: {followup_col}")

            # Run the follow-up query using the main result as context.
            try:
                fr = run_followup_query(
                    index=index,
                    llm=llm,
                    raw_df=raw_df,
                    main_result=main_result,
                    followup_query=followup_query,
                    top_k=top_k,
                    run_eval=run_eval,
                )
            except Exception as e:
                status.error(f"Failed follow-up for {question_id} ({followup_col}): {e}")
                raise

            # Extract a cleaner follow-up number from names like followup_1.
            followup_number = (
                followup_col.split("_", 1)[1]
                if followup_col.lower().startswith("followup_") and "_" in followup_col
                else followup_col
            )

            # Add follow-up metadata to the result dictionary.
            fr["followup_column"] = followup_col
            fr["followup_number"] = followup_number

            followup_results.append(fr)

            # Add one summary row for this follow-up answer.
            followup_summary_rows.append(
                {
                    "batch_id": batch_id,
                    "question_id": question_id,
                    "followup_column": followup_col,
                    "followup_number": followup_number,
                    "main_run_id": fr["main_run_id"],
                    "followup_run_id": fr["followup_run_id"],
                    "query_llm_model": query_llm_model,
                    "main_query": main_query,
                    "main_answer": main_result["response_text"],
                    "followup_query": followup_query,
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
                }
            )

            # Save retrieved context rows used for this follow-up answer.
            followup_context_rows.extend(
                [
                    {
                        "batch_id": batch_id,
                        "question_id": question_id,
                        "followup_column": followup_col,
                        "followup_number": followup_number,
                        **row,
                    }
                    for row in fr["context_rows"]
                ]
            )

            # Build evaluator-ready rows for follow-up answers.
            followup_evaluator_rows.extend(
                [
                    {
                        "followup_column": followup_col,
                        "followup_number": followup_number,
                        **row,
                    }
                    for row in build_followup_evaluator_rows(
                        batch_id=batch_id,
                        question_id=question_id,
                        query_llm_model=query_llm_model,
                        main_query=main_query,
                        main_answer=main_result["response_text"],
                        followup_query=followup_query,
                        followup_answer=fr["followup_answer"],
                        metric_scores=fr["metric_scores"],
                        raw_df=raw_df,
                        context_nodes=fr["context_nodes"],
                        followup_run_id=fr["followup_run_id"],
                        main_run_id=fr["main_run_id"],
                        answer_started_at=fr["answer_started_at"],
                        answer_finished_at=fr["answer_finished_at"],
                        answer_duration_seconds=fr["answer_duration_seconds"],
                    )
                ]
            )

            # Update progress after completing this follow-up question.
            current_step += 1
            progress.progress(min(current_step / max(total_steps, 1), 1.0))

        # Save all follow-up outputs for this main question.
        save_single_followup_runs(question_dir, followup_results)

    # Show final Streamlit status.
    status.success("Batch run complete.")
    progress.progress(1.0)

    # Convert all collected rows into dataframes.
    main_summary_df = pd.DataFrame(main_summary_rows)
    main_evidence_df = pd.DataFrame(main_evidence_rows)
    main_eval_df = pd.DataFrame(main_evaluator_rows)
    followup_summary_df = pd.DataFrame(followup_summary_rows)
    followup_context_df = pd.DataFrame(followup_context_rows)
    followup_eval_df = pd.DataFrame(followup_evaluator_rows)

    # Combine main and follow-up evaluator rows into one results dataframe.
    all_results_df = build_all_results_df(main_eval_df, followup_eval_df)

    # Create a manifest file that records key details about this batch run.
    batch_manifest = {
        "batch_id": batch_id,
        "batch_timestamp": batch_timestamp,
        "query_llm_model": query_llm_model,
        "fixed_index_llm_model": FIXED_INDEX_LLM_MODEL,
        "fixed_embed_model": FIXED_EMBED_MODEL,
        "fixed_index_dir": str(getattr(index.storage_context, "persist_dir", "")),
        "num_questions": len(question_records),
        "num_main_runs": len(main_summary_rows),
        "num_followup_runs": len(followup_summary_rows),
        "saved_dir": str(batch_dir),
        "graph_screenshots_dir": str(graph_gallery_dir),
    }

    # RAGAS metric columns expected in the final dataframe.
    score_cols = [
        "Answer Relevancy",
        "Faithfulness",
        "Context Relevance",
        "Response Groundedness",
    ]

    # Check whether any rows are missing RAGAS scores.
    # This is useful for debugging failed or incomplete evaluation runs.
    if not all_results_df.empty:
        existing_score_cols = [
            col for col in score_cols
            if col in all_results_df.columns
        ]

        if existing_score_cols:
            missing_score_rows = all_results_df[
                all_results_df[existing_score_cols].isna().any(axis=1)
            ]

            if not missing_score_rows.empty:
                print("Rows with missing RAGAS scores:")
                print(
                    missing_score_rows[
                        [
                            "result_type",
                            "question_id",
                            "main_query",
                            "followup_query",
                            *existing_score_cols,
                        ]
                    ]
                )

    # Save the batch manifest and combined output CSV.
    save_batch_outputs(
        batch_dir=batch_dir,
        batch_manifest=batch_manifest,
        all_results_df=all_results_df,
    )

    # Return all important batch outputs so the Streamlit app can display them.
    return {
        "batch_manifest": batch_manifest,
        "batch_dir": batch_dir,
        "main_summary_df": main_summary_df,
        "main_evidence_df": main_evidence_df,
        "main_eval_df": main_eval_df,
        "followup_summary_df": followup_summary_df,
        "followup_context_df": followup_context_df,
        "followup_eval_df": followup_eval_df,
        "all_results_df": all_results_df,
        "last_main_result": last_main_result,
        "main_results_by_question": main_results_by_question,
    }