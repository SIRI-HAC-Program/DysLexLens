# Knowledge-graph html

This folder contains the knowledge graph for main research question— the subset of entities and relations
extracted from the Reddit dyslexia corpus that are relevant to research questions.

## View the graph

If GitHub does not render the interactive HTML directly, download the file and open it in a web browser.
```text
knowledge_graph/RQ1/graph_RQ1.html
```



## How it was generated

The subgraph is built using **LlamaIndex's `PropertyGraphIndex`**:

1. Reddit posts/comments relevant to research questions are retrieved from the indexed corpus.
2. The LLM extracts entity–relation–entity triples (e.g. `Dyslexic —Is(1)→ 14 years old`) from the retrieved text chunks.
3. Triples are deduplicated and aggregated, with edge labels showing relation type and occurrence count, and node size/tooltip showing mention frequency.
4. The resulting graph is rendered to a standalone HTML file using PyVis for interactive viewing — no server required, just open it in a browser.
