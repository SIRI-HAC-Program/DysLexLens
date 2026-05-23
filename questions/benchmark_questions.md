# Benchmark Questions Used in the Paper

This document lists the benchmark questions used in the DysLexLens evaluation. The benchmark was designed to support reproducible evaluation of the framework across the main themes explored in the paper.

The benchmark contains 30 questions in total:

- 5 main research questions
- 25 follow-up questions
- 5 follow-up questions for each main research question

These questions were used for the RAGAS framework benchmarking and for generating evidence-traceable responses from the Reddit-based dyslexia corpus.

---

## RQ1

**Main research question**

What learning-related use cases for AI tools are described by dyslexic learners in online discussions?

**Follow-up questions**

1. Which AI tools are mentioned most frequently?
2. What learning tasks are commonly supported by these tools?
3. Do users describe AI as replacing or complementing traditional support methods?
4. Are there differences between school-related and workplace-related use cases?
5. What accessibility-related functions are discussed most often?

---

## RQ2

**Main research question**

What benefits and failure modes are reported when AI tools are used for different learning tasks?

**Follow-up questions**

1. What benefits are most commonly reported?
2. What limitations or frustrations are discussed?
3. Are there concerns about over-reliance on AI tools?
4. Which learning tasks appear most difficult for AI support?
5. Do users discuss inaccurate or misleading AI outputs?

---

## RQ3

**Main research question**

Under what conditions are AI tools perceived as helpful, supportive, or inclusive for dyslexic learners?

**Follow-up questions**

1. What factors make AI tools easier to use?
2. Do users discuss personalisation or adaptability?
3. Are emotional or confidence-related benefits mentioned?
4. What role does usability play in perceived effectiveness?
5. Are there differences between beginner and experienced users?

---

## RQ4

**Main research question**

How are AI-based supports discussed in relation to broader educational challenges, including institutional accommodations and personal coping strategies?

**Follow-up questions**

1. Are schools or universities discussed as supportive of AI use?
2. How are formal accommodations such as IEPs mentioned?
3. Do users describe AI as part of their coping strategies?
4. Are teachers or parents discussed in relation to AI-supported learning?
5. What institutional barriers are reported?

---

## RQ5

**Main research question**

How have discussions of AI tools among dyslexic learners changed over time in terms of prevalence, tone, and perceived role in learning support?

**Follow-up questions**

1. Do users describe increased AI adoption over time?
2. Are perceptions of AI becoming more positive or negative?
3. What trends appear in discussions of accessibility tools?
4. Are newer AI tools discussed differently from older technologies?
5. Do users mention changing attitudes in education or workplaces?

---

## Notes for Reproducibility

The questions in this file correspond to the benchmark questions used in the evaluation pipeline. The machine-readable version is provided in `benchmark_questions.csv`.

For query robustness analysis, see `query_robustness_variants.csv`, which includes original, paraphrased, and keyword-perturbed versions of the benchmark questions.
