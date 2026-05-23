This repository presents **DysLexLens**, a low-resource LLM framework for examining how dyslexic learners describe their learning challenges, coping strategies, support needs, and use of AI tools within broader educational and social contexts over time.

DysLexLens supports the full workflow from targeted online data collection to query-based reasoning, evidence tracing, and response evaluation. Although this repository focuses on dyslexia-related Reddit discussions, the framework can be adapted to other forms of online forum or social media data.

To build a topic-focused corpus for downstream analysis, DysLexLens applies a concept dictionary-based filtering method. It then constructs a reusable Knowledge Graph (KG) from the final filtered corpus. Given a user query, DysLexLens retrieves relevant semantic triples from the KG and supporting text passages from the corpus. It combines graph-based semantic interpretation with source-grounded response generation, allowing users to ask main research questions and follow-up questions.

The framework also includes a three-stage evidence-tracing pipeline to support fact-checking and provenance inspection. This pipeline links generated claims to cited source chunks, supporting evidence, and original Reddit records where available.

In addition to automatic RAGAS-based evaluation and query robustness analysis, the repository provides a rubric-based human assessment guideline in the `evaluation/human_provenance_audit/` folder. This supports evaluation of whether generated responses are relevant, factually consistent, grounded in retrieved evidence, and interpretable through traceable provenance.
