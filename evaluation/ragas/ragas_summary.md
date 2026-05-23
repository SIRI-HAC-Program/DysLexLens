# RAGAS Evaluation Summary

This file summarises the RAGAS-based evaluation results for DysLexLens across the benchmark questions used in the paper.

The evaluation included 30 generated responses:

- 5 main research-question responses
- 25 follow-up responses

Each response was evaluated using four RAGAS metrics:

| Metric | Purpose |
|---|---|
| Response Relevancy | Measures how well the generated response addresses the question. |
| Faithfulness | Measures whether the response is factually consistent with the retrieved context. |
| Context Relevance | Measures whether the retrieved context is relevant to the question. |
| Response Groundedness | Measures whether generated claims are supported by the retrieved evidence. |

## Evaluation Setup

All responses were generated using the same retrieval and evaluation configuration to support fair comparison across questions.

| Setting | Value |
|---|---|
| Query-time LLM | `openai/gpt-4o-mini` |
| Fixed index LLM | `openai/gpt-4o-mini` |
| Embedding model | `text-embedding-3-small` |
| Similarity top-k | 3 |
| Citation chunk size | 512 tokens |
| Number of evaluated responses | 30 |

## Summary Results

| Response Set | n | Response Relevancy | Faithfulness | Context Relevance | Response Groundedness |
|---|---:|---:|---:|---:|---:|
| All responses | 30 | 0.75 (0.23) | 0.52 (0.36) | 0.40 (0.28) | 0.43 (0.24) |
| Main RQs | 5 | 0.87 (0.13) | 0.40 (0.24) | 0.45 (0.27) | 0.35 (0.22) |
| Follow-ups | 25 | 0.72 (0.24) | 0.54 (0.38) | 0.39 (0.28) | 0.45 (0.24) |

One Faithfulness score was unavailable for a follow-up response, so Faithfulness for all responses and follow-ups was calculated using the available scored responses.

## Main Research-Question Scores

| RQ | Response Relevancy | Faithfulness | Context Relevance | Response Groundedness |
|---|---:|---:|---:|---:|
| RQ1 | 0.94 | 0.17 | 0.75 | 0.50 |
| RQ2 | 0.93 | 0.63 | 0.50 | 0.50 |
| RQ3 | 0.87 | 0.67 | 0.50 | 0.00 |
| RQ4 | 0.65 | 0.18 | 0.50 | 0.25 |
| RQ5 | 0.95 | 0.33 | 0.00 | 0.50 |
| Mean | 0.87 | 0.40 | 0.45 | 0.35 |


## File Description

The file `ragas_results_main_and_followups.csv` contains one row per evaluated response after deduplication at the response level.

It includes:

| Column | Description |
|---|---|
| `response_type` | Whether the response is a main research-question response or a follow-up response. |
| `question_id` | Research question identifier, such as `RQ1`. |
| `followup_number` | Follow-up number, where applicable. |
| `question_label` | Combined label, such as `RQ1` or `RQ1_F1`. |
| `question_text` | The question used for evaluation. |
| `Answer Relevancy` | RAGAS Response Relevancy score. |
| `Faithfulness` | RAGAS Faithfulness score. |
| `Context Relevance` | RAGAS Context Relevance score. |
| `Response Groundedness` | RAGAS Response Groundedness score. |

ral questions, and educational interpretations.
