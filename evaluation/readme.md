# Evaluation

This folder contains the materials used to evaluate DysLexLens, combining automated metrics with human review.

## Components

### 1. Quantitative RAGAS assessment
[`quantitative_ragas_assessment/`](./quantitative_ragas_assessment/)

Scores DysLexLens responses (main and follow-up questions) on four RAGAS metrics: Response Relevancy, Faithfulness, Context Relevance, and Response Groundedness — assessing whether responses are relevant, factually consistent with retrieved context, supported by relevant evidence, and grounded in source material.

- `ragas_results_main_and_followups.csv`
- `ragas_summary.md`

### 2. Quantitative query robustness assessment
[`quantitative_query_robustness_assessment/`](./quantitative_query_robustness_assessment/)

Tests whether DysLexLens stays stable when the same question is asked in different ways — original, paraphrased, and keyword-perturbed variants.

- `query_robustness_all30_variants.csv`
- `query_robustness_scores.csv`
- `query_robustness_summary.md`

### 3. Qualitative human-grounded response quality assessment
[`qualitative_human_grounded_response_quality_assessment/`](./qualitative_human_grounded_response_quality_assessment/)

Human review checking whether generated claims are present in the original source, supported by a relevant source chunk, and traceable through provenance.

- `human_evaluation_protocol.md`
- `human_audit_completed.csv`
- `audit_summary.md`
