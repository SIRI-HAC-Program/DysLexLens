# Human-Grounded Provenance Audit Summary

This file summarises the completed human-grounded provenance audit for DysLexLens. The audit was conducted to assess whether generated claims could be traced back to cited evidence and whether the cited evidence supported the specific claim being evaluated.

The audit reviewed 100 claim-level rows from the generated evaluation outputs. Each row represented a claim candidate linked to provenance information, including cited evidence, source chunk, Reddit identifier, and the original post where available. The reviewed sample included both main research-question responses and follow-up responses.

## Audit Scope

| Category | Count |
|---|---:|
| Total audited rows | 100 |
| Main research-question rows | 11 |
| Follow-up rows | 89 |

The audited rows covered all five research questions.

| Research Question | Audited Rows |
|---|---:|
| RQ1 | 30 |
| RQ2 | 14 |
| RQ3 | 19 |
| RQ4 | 22 |
| RQ5 | 15 |

## Evaluation Dimensions

Each claim-level row was assessed using three dimensions:

1. **Accuracy in original source**: whether the cited phrase or evidence appeared in the original Reddit source.
2. **Support strength**: how strongly the cited evidence supported the specific generated claim.
3. **Interpretative utility**: whether the provenance information allowed an independent reader to verify and assess the claim.

Support strength was scored on a three-point scale:

| Score | Meaning |
|---|---|
| 1 | Weak or speculative support |
| 2 | Acceptable support |
| 3 | Strong support |

## Results

### Accuracy in Original Source

| Accuracy Category | Count | Percentage |
|---|---:|---:|
| Yes | 39 | 39% |
| Partial | 55 | 55% |
| No | 6 | 6% |


### Support Strength

| Support Strength | Count | Percentage |
|---|---:|---:|
| 1: Weak or speculative | 18 | 18% |
| 2: Acceptable support | 61 | 61% |
| 3: Strong support | 21 | 21% |


### Interpretative Utility

| Interpretative Utility | Count | Percentage |
|---|---:|---:|
| High | 14 | 14% |
| Medium | 61 | 61% |
| Low | 25 | 25% |


## Main and Follow-up Comparison


| Response Type | Yes | Partial | No |
|---|---:|---:|---:|
| Main | 10 | 1 | 0 |
| Follow-up | 29 | 54 | 6 |


| Response Type | Weak Support | Acceptable Support | Strong Support |
|---|---:|---:|---:|
| Main | 3 | 4 | 4 |
| Follow-up | 15 | 57 | 17 |

