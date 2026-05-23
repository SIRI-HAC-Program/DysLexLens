# services/evidence_service.py

# Import helper functions used to process answer text and source chunks.
from utils.text_utils import (
    parse_sentence_citations,
    strip_kg_triples,
)

# Import prompt templates used for evidence alignment and follow-up answers.
from prompts.templates import EVIDENCE_PROMPT, build_followup_prompt


def align_evidence_for_response(llm, answer: str, source_nodes: list) -> list[dict]:
    """
    Align each cited sentence in the generated answer with supporting evidence.

    This function:
    - Splits the generated answer into sentence-level claims.
    - Finds the citation numbers used in each sentence.
    - Retrieves the matching source chunks.
    - Sends the sentence and cited chunks to the LLM.
    - Asks the LLM to identify the specific supporting evidence.

    Args:
        llm: The language model used to complete the evidence-alignment prompt.
        answer: The generated answer text that contains citations.
        source_nodes: The retrieved source nodes used to generate the answer.

    Returns:
        A list of dictionaries. Each dictionary contains:
        - sentence: the sentence from the generated answer
        - citations: citation IDs used in that sentence
        - evidence: evidence alignment result or fallback message
    """

    # Store all evidence-alignment results.
    results = []

    # Parse the answer into sentence-level items with their citations.
    for item in parse_sentence_citations(answer):
        sentence = item["sentence"]
        citations = item["citations"]

        # If the sentence has no citation, record that no evidence was provided.
        if not citations:
            results.append({
                "sentence": sentence,
                "citations": [],
                "evidence": "No citation.",
            })
            continue

        # Store the source chunks linked to the cited citation IDs.
        chunk_blocks = []

        # Match each citation ID to its corresponding source node.
        for cid in citations:
            # Citation numbers are 1-based, but Python lists are 0-based.
            if 0 <= cid - 1 < len(source_nodes):
                node = source_nodes[cid - 1]

                # LlamaIndex nodes may store text in node.node.text or node.text.
                raw_text = node.node.text if hasattr(node, "node") else node.text

                # Remove knowledge graph triples before sending the chunk to the LLM.
                cleaned_text = strip_kg_triples(raw_text)

                # Add the cleaned chunk with its citation label.
                chunk_blocks.append(f"CHUNK [{cid}]:\n{cleaned_text}")

        # If none of the citation IDs matched available source nodes, record this issue.
        if not chunk_blocks:
            results.append({
                "sentence": sentence,
                "citations": citations,
                "evidence": "Cited chunks not found.",
            })
            continue

        # Build the evidence-alignment prompt using the sentence and cited chunks.
        prompt = EVIDENCE_PROMPT.format(
            sentence=sentence,
            chunks_text="\n\n".join(chunk_blocks),
        )

        # Ask the LLM to identify the evidence that supports the sentence.
        evidence = llm.complete(prompt).text.strip()

        # Save the evidence-alignment result for this sentence.
        results.append({
            "sentence": sentence,
            "citations": citations,
            "evidence": evidence,
        })

    # Return all sentence-level evidence-alignment results.
    return results


def ask_followup_with_citation(llm, source_nodes: list, question: str) -> str:
    """
    Answer a follow-up question using the provided source nodes as context.

    This function:
    - Converts retrieved source nodes into citation-labelled context chunks.
    - Builds a follow-up prompt using those chunks and the follow-up question.
    - Sends the prompt to the LLM.
    - Returns the generated follow-up answer.

    Args:
        llm: The language model used to answer the follow-up question.
        source_nodes: The source nodes used as context for the follow-up answer.
        question: The follow-up question asked by the user.

    Returns:
        The generated follow-up answer as a string.
    """

    # Store context chunks with custom citation IDs such as C1, C2, C3.
    context_chunks = []

    # Convert each source node into a clean text chunk with a citation ID.
    for i, node in enumerate(source_nodes):
        # LlamaIndex nodes may store text in node.node.text or node.text.
        raw_text = node.node.text if hasattr(node, "node") else node.text

        # Remove knowledge graph triples to keep only readable source text.
        cleaned_text = strip_kg_triples(raw_text)

        # Add the cleaned chunk to the context list with a follow-up citation ID.
        context_chunks.append({
            "id": f"C{i + 1}",
            "text": cleaned_text,
        })

    # Build one context string with citation-labelled chunks.
    # Example format:
    # [C1] source text...
    #
    # [C2] source text...
    context_str = "\n\n".join(
        f"[{chunk['id']}] {chunk['text']}"
        for chunk in context_chunks
    )

    # Build the follow-up prompt using the prepared context and question.
    prompt = build_followup_prompt(
        context_str=context_str,
        question=question,
    )

    # Generate and return the follow-up answer.
    return llm.complete(prompt).text.strip()