# Questions

This folder contains the benchmark questions and query variants used in the DysLexLens paper and evaluation pipeline.

The questions are provided in both human-readable and machine-readable formats so that reviewers can inspect the benchmark design and reproduce the evaluation process.

## Files

| File | Description |
|---|---|
| `benchmark_questions.md` | Human-readable list of the main research questions and follow-up questions used in the paper. |
| `benchmark_questions.csv` | Machine-readable version of the benchmark questions used by the DysLexLens batch evaluation tool. |
| `query_robustness_variants.csv` | Query robustness variants, including original, paraphrased, and keyword-perturbed versions of the questions. |

## Benchmark Design

The benchmark includes 30 questions in total:

- 5 main research questions
- 25 follow-up questions
- 5 follow-up questions for each main research question

These questions were used to evaluate DysLexLens across the main themes of the study, including AI use cases, benefits and limitations, supportive conditions, educational challenges, and changes over time.

## Query Robustness Variants

The query robustness file includes three versions of each query:

- `original`: the original benchmark question
- `paraphrased`: a rewritten version with the same meaning
- `keyword_perturbed`: a version with modified or expanded keywords

These variants were used to test how stable the system is when the wording of the question changes.To generate these variants GPT5.5 Pro is used.

## How These Files Are Used

The `benchmark_questions.csv` file can be uploaded into the DysLexLens Streamlit tool when running batch evaluation. The tool uses the main research questions and follow-up questions to generate responses, retrieve evidence, calculate RAGAS scores, and export evaluation outputs.


