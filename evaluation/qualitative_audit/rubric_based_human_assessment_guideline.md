
# Rubric_based Human Assessment Guideline

## Purpose of the Evaluation

This guide provides instructions for human evaluators assessing model-generated answers using the result file.

The evaluation follows a claim-level qualitative analysis protocol designed to complement automatic metrics, such as RAGAS, in line with the evaluation methodology used for CIKM 2026.

Each row in the CSV corresponds to a single claim candidate extracted from a model-generated answer, together with its associated provenance and evidence.

## Important Clarification

Rows may appear similar, but they are not duplicates.

It is common for multiple rows to:

- originate from the same generated answer
- cite the same Reddit post, identified by `reddit_id`
- reference the same evidence chunk

This is intentional. A single source may support multiple distinct claims, and each claim must be evaluated independently.

## Overview of the Evaluation Process

For each sampled answer, evaluators must assess each row independently using the following three steps:

1. Claim decomposition
2. Provenance tracing
3. Verification

Evaluators should complete all steps for one row before moving to the next row, even when rows share the same source or evidence.

## Step 1: Claim Decomposition

### Relevant columns

- `claim_candidate`
- `full_answer` for context only

### Task

Treat the `claim_candidate` as a candidate atomic claim.

- Determine whether the claim expresses a single, indivisible proposition.
- If the claim contains multiple ideas, refine it into a single atomic claim.
- Record the refined claim in the column `atomic_claim_after_human_decomposition`.

### Example

**Claim candidate:**

> The source discusses AI tools that help with writing challenges and improve confidence.

This can be decomposed into two atomic claims:

1. The source discusses AI tools that help with writing challenges.
2. The source discusses AI tools that improve learner confidence.

## Step 2: Provenance Tracing

### Relevant columns

- `source-chunk index_id`
- `reddit_id`
- `verbatim_evidence`
- `evidence_alignment_block`
- `source_chunk`
- `full_post`

### Task

For each claim:

1. Identify the verbatim evidence phrase cited for the claim.
2. Confirm that this phrase appears in the Reddit post identified by `reddit_id`.
3. Verify that the evidence supports the specific claim, not merely the answer in general.

### Example

**Claim:**

> IEPs provide legally binding educational accommodations.

**Evidence:**

> If you have a diagnosis then you will almost certainly be given legally binding accommodations by the school.

**Assessment:**

The provenance is direct, explicit, and traceable.

## Step 3: Verification

Each claim-evidence pair must be evaluated across three dimensions:

1. Accuracy
2. Support strength
3. Interpretative utility

## 3.1 Accuracy

### Question

Is the cited phrase present in the original source?

### Rating options

- **Yes:** The evidence clearly appears in the source.
- **Partial:** The evidence partially appears in the source.
- **No:** The evidence does not appear in the source or contradicts the source.

Record the assessment in the column `accuracy_present_in_original_source`.

## 3.2 Support Strength

### Evaluation question

How strongly does the cited evidence support the specific claim being evaluated?

Evaluators must assign a score on a three-point Likert scale. The score should reflect how directly the evidence supports the claim.

| Score | Interpretation |
|---:|---|
| 1 | Weak or speculative support |
| 2 | Acceptable support |
| 3 | Strong support |

Record the assigned score in the column `support_strength_1_to_3`.

**Important:** The current CSV column name may still say `support_strength_1_to_3`, but evaluators should use only the 1 to 3 scale shown above.

### Important note

Claims from the same source, such as the same Reddit post or source-chunk index, may receive different support strength scores. Scores depend on how directly each individual claim is supported by the cited evidence.

### Illustrative example

**Claim candidate:**

> The source describes AI tools as helping students overcome writing challenges.

**Cited verbatim evidence:**

> We built him a custom tool that helped him get through the word processor frustration.

**Assigned score:**

3: Strong support

**Rationale:**

The evidence explicitly states that a custom tool was built to address writing-related frustration. The claim requires little or no inference beyond the quoted text.

### Contrastive example from the same source

**Claim candidate:**

> The source suggests that AI tools improve learner confidence.

**Cited evidence:**

> He has had a hard time, feeling frustrated and demotivated at times.

**Assigned score:**

1: Weak or speculative support

**Rationale:**

The evidence describes emotional difficulty, but it does not explicitly state that AI tools improve confidence. The claim relies on inference rather than direct support.

### Key guidance for evaluators

Support strength must be judged per claim, not per source. Even when multiple claims cite the same evidence, each claim may differ in how strongly it is supported.

## 3.3 Interpretative Utility

### Question

Does the provenance information enable an independent reader to verify and critically assess the claim?

### Rating options

- **High:** Evidence is explicit and unambiguous.
- **Medium:** Evidence exists but requires interpretation.
- **Low:** Evidence is vague or weakly linked.

Record the judgement, with optional brief notes, in the column `interpretative_utility_yes_no_or_comment`.

## Why Similar Rows Must Be Evaluated Separately

A single Reddit post may contain multiple statements supporting different claims, such as:

- AI tools help with writing challenges.
- Tools support longer-form writing.
- IEPs provide legally binding accommodations.
- Assistive technologies are framed metaphorically, such as "crutches".

Although these claims may cite the same evidence, they represent distinct propositions and must be verified independently.

## Mapping to the CIKM 2026 Evaluation Protocol

This evaluation implements the following methodology:

1. **Claim decomposition** through `claim_candidate` and `atomic_claim_after_human_decomposition`.
2. **Provenance tracing** through `source-chunk index_id`, `reddit_id`, and the evidence fields.
3. **Verification** through accuracy, support strength, and interpretative utility judgements.

## Final Reminder

Do not merge rows, even if they appear similar.

Each row represents a distinct claim that must be evaluated independently.

