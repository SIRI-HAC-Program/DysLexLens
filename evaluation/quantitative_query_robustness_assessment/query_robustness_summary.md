# Query Robustness Summary

This file summarises the query robustness results for DysLexLens. The aim of this analysis is to examine whether the system produces stable RAGAS results when the same benchmark questions are written in different ways.

The query robustness analysis used three versions of each question:

- Original question
- Paraphrased question
- Keyword-perturbed question

## Mean RAGAS Scores by Query Variant

| Query variant | Response Relevancy | Faithfulness | Context Relevance | Response Groundedness |
|---|---:|---:|---:|---:|
| Original | 0.75 | 0.52 | 0.40 | 0.43 |
| Paraphrased | 0.58 | 0.55 | 0.31 | 0.25 |
| Keyword-perturbed | 0.34 | 0.66 | 0.33 | 0.28 |

