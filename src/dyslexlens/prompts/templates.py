# prompts/templates.py

# Import PromptTemplate from LlamaIndex.
# PromptTemplate is used to define reusable prompts with placeholders.
from llama_index.core import PromptTemplate


# Main question-answering prompt.
# This prompt is used by the citation query engine when answering main research questions.
MAIN_QA_PROMPT = PromptTemplate(
    """
You are a strict retrieval-based QA system.

RULES:
1. Answer ONLY using the provided context.
2. Every claim MUST include a citation like [1], [2].
3. Do NOT use outside knowledge.
4. If the answer is not in the context, say:
"I cannot find this information in the provided context."
5. Be concise and precise.

CONTEXT:
{context_str}

QUESTION:
{query_str}

ANSWER:
""".strip()
)


# Evidence-alignment prompt.
# This prompt asks the LLM to find exact supporting evidence for a generated answer sentence.
# It is used after an answer is generated, to check whether each cited sentence is supported
# by the cited source chunks.
EVIDENCE_PROMPT = PromptTemplate(
    """
You are an explainability assistant. Find the EXACT verbatim text from the
CHUNKS below that supports the ANSWER SENTENCE.

STRICT RULES:
- Only quote text that appears word-for-word in the chunks.
- Do NOT use outside knowledge.
- If a chunk has no relevant text write: Not found in this chunk.
- Keep each evidence excerpt to one phrase or sentence.

ANSWER SENTENCE:
{sentence}

{chunks_text}

Reply in this exact format, one block per chunk:

CHUNK [{{chunk_id}}]:
  Evidence : <verbatim quote, or "Not found in this chunk.">
  Reason   : <one sentence explaining how it supports the answer>
""".strip()
)


def build_followup_prompt(context_str: str, question: str) -> str:
    """
    Build the follow-up QA prompt using chunk-labelled context.

    The follow-up context is expected to contain chunk labels such as:
    [C1], [C2], [C3], ...

    Args:
        context_str: The retrieved context chunks formatted with chunk labels.
        question: The follow-up question to answer.

    Returns:
        A prompt string that asks the LLM to answer using only the provided context.
    """

    # Build and return the follow-up prompt.
    # The prompt tells the model to:
    # - use only the provided context,
    # - cite chunk IDs such as [C1] and [C2],
    # - avoid outside knowledge,
    # - cite every claim.
    return f"""
Answer the question using ONLY the context below.

Context:
{context_str}

Question:
{question}

Rules:
- Cite the chunk IDs like [C1], [C2]
- Every claim must include a citation
- Do NOT use outside knowledge
""".strip()