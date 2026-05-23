# utils/text_utils.py

# Import regular expressions.
# This is used to find citation patterns such as [1], [2], [C1], and [C2].
import re

# Import type hints for clearer function inputs and outputs.
from typing import List, Dict, Set


def get_used_citations(text: str) -> Set[int]:
    """
    Extract numeric citation markers from text.

    Example:
        "This claim is supported by evidence [1] and [2]."

    Returns:
        {1, 2}
    """

    # If the text is empty or None, return an empty set.
    if not text:
        return set()

    # Find all numeric citation markers such as [1], [2], or [12].
    # Convert each matched number from string to integer.
    return {int(n) for n in re.findall(r"\[(\d+)\]", text)}


def get_used_subquery_citations(text: str) -> Set[str]:
    """
    Extract follow-up citation markers from text.

    Follow-up answers use citation markers such as [C1], [C2], and [C3].

    Example:
        "This answer uses the follow-up context [C1]."

    Returns:
        {"C1"}
    """

    # If the text is empty or None, return an empty set.
    if not text:
        return set()

    # Find all citation markers that follow the C-style format.
    # Examples: [C1], [C2], [C12].
    return set(re.findall(r"\[(C\d+)\]", text))


def strip_kg_triples(text: str) -> str:
    """
    Remove knowledge graph triple boilerplate from LlamaIndex node text.

    Some retrieved node text may include generated knowledge graph facts.
    This function tries to remove that extra section and keep the original
    source content for cleaner display and evaluation.
    """

    # If the input text is empty or None, return an empty string.
    if not text:
        return ""

    # Remove the boilerplate section that starts with:
    # "Source X:"
    # "Here are some facts extracted from the provided text:"
    #
    # The regex removes this generated KG-triple block while trying to keep
    # the original source content that follows.
    cleaned = re.sub(
        r"Source\s+\d+:\s*\n+Here are some facts extracted from the provided text:.*?(?=\n[A-Z\[])",
        "",
        text,
        flags=re.DOTALL,
    ).strip()

    # If cleaning produced useful text, return it.
    # Otherwise, return the original text to avoid accidentally deleting content.
    return cleaned if cleaned else text


def parse_sentence_citations(answer: str) -> List[Dict]:
    """
    Split a main answer into sentence-level claims and extract numeric citations.

    Main answers use citation markers such as [1], [2], and [3].

    Returns:
        [
            {
                "sentence": "claim text",
                "citations": [1, 2]
            }
        ]
    """

    # If the answer is empty or None, return an empty list.
    if not answer:
        return []

    # Split the answer into sentence-like parts.
    # This splits after ., !, or ? when the next sentence starts with a capital letter.
    raw_sentences = re.split(
        r"(?<=[.!?])\s+(?=[A-Z])",
        answer.strip(),
    )

    # Store parsed sentence records.
    results = []

    # Buffer stores sentence fragments without citations.
    # These fragments are joined with the next cited sentence.
    buffer: List[str] = []

    # Process each sentence-like part.
    for sent in raw_sentences:
        # Remove extra spaces.
        sent = sent.strip()

        # Skip empty sentence parts.
        if not sent:
            continue

        # Extract numeric citation IDs from the sentence.
        citations = [int(n) for n in re.findall(r"\[(\d+)\]", sent)]

        # Remove citation markers from the sentence text.
        # This keeps only the claim text.
        clean = re.sub(r"\s*\[\d+\]", "", sent).strip()

        # If the sentence has citations, save it as a claim.
        if citations:
            # Join any previous uncited text with the current cited sentence.
            combined = " ".join(buffer + [clean]).strip()

            # Add the parsed sentence and its citations.
            results.append({
                "sentence": combined,
                "citations": citations,
            })

            # Clear the buffer after it has been used.
            buffer = []

        else:
            # If the sentence has no citation, store it temporarily.
            # It may belong to the next cited sentence.
            buffer.append(clean)

    # If any uncited text remains at the end, save it with no citations.
    if buffer:
        results.append({
            "sentence": " ".join(buffer).strip(),
            "citations": [],
        })

    # Return all parsed sentence-level citation records.
    return results


def parse_subquery_sentence_citations(answer: str) -> List[Dict]:
    """
    Split a follow-up answer into sentence-level claims
    and extract follow-up citations.

    Follow-up answers use citation markers such as [C1], [C2], and [C3].

    Returns:
        [
            {
                "sentence": "claim text",
                "citations": ["C1", "C2"]
            }
        ]
    """

    # If the answer is empty or None, return an empty list.
    if not answer:
        return []

    # Split the answer into sentence-like parts.
    # This follows the same sentence-splitting rule used for main answers.
    raw_sentences = re.split(
        r"(?<=[.!?])\s+(?=[A-Z])",
        answer.strip(),
    )

    # Store parsed follow-up sentence records.
    results = []

    # Buffer stores sentence fragments without citations.
    buffer: List[str] = []

    # Process each sentence-like part.
    for sent in raw_sentences:
        # Remove extra spaces.
        sent = sent.strip()

        # Skip empty sentence parts.
        if not sent:
            continue

        # Extract follow-up citation IDs such as C1, C2, or C12.
        citations = re.findall(r"\[(C\d+)\]", sent)

        # Remove follow-up citation markers from the sentence text.
        clean = re.sub(r"\s*\[(C\d+)\]", "", sent).strip()

        # If the sentence has follow-up citations, save it as a claim.
        if citations:
            # Join previous uncited text with the current cited sentence.
            combined = " ".join(buffer + [clean]).strip()

            # Add the parsed sentence and its C-style citations.
            results.append({
                "sentence": combined,
                "citations": citations,
            })

            # Clear the buffer after it has been used.
            buffer = []

        else:
            # If the sentence has no citation, store it temporarily.
            buffer.append(clean)

    # If any uncited text remains at the end, save it with no citations.
    if buffer:
        results.append({
            "sentence": " ".join(buffer).strip(),
            "citations": [],
        })

    # Return all parsed follow-up sentence-level citation records.
    return results