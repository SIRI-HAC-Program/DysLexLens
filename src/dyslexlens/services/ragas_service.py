# services/ragas_service.py

# Import the asynchronous OpenAI-compatible client.
# This is used to connect to OpenRouter through an OpenAI-like API.
from openai import AsyncOpenAI

# Import RAGAS helper factories for creating the LLM and embedding objects.
from ragas.llms import llm_factory
from ragas.embeddings.base import embedding_factory

# Import the RAGAS metrics used to evaluate generated responses.
from ragas.metrics.collections import (
    AnswerRelevancy,
    Faithfulness,
    ContextRelevance,
    ResponseGroundedness,
)

# Import project configuration values.
# OPENROUTER_API_BASE stores the OpenRouter API endpoint.
# FIXED_EMBED_MODEL stores the embedding model used for evaluation.
from config import OPENROUTER_API_BASE, FIXED_EMBED_MODEL


# Global RAGAS objects.
# These are initialised once using init_ragas() and then reused for scoring.
_ragas_client = None
_ragas_llm = None
_ragas_embedding = None


def init_ragas(api_key: str, eval_model: str):
    """
    Initialise the RAGAS evaluation components.

    This function:
    - Creates an asynchronous OpenRouter client.
    - Creates the RAGAS LLM used for evaluation.
    - Creates the embedding model used by metrics such as Answer Relevancy.

    Args:
        api_key: The OpenRouter API key.
        eval_model: The model name used as the evaluator LLM.
    """

    # Tell Python that we want to update the global RAGAS objects.
    global _ragas_client, _ragas_llm, _ragas_embedding

    # Create the asynchronous OpenAI-compatible client.
    # OpenRouter uses an OpenAI-like API, so AsyncOpenAI can be used here.
    _ragas_client = AsyncOpenAI(
        api_key=api_key,
        base_url=OPENROUTER_API_BASE,
    )

    # Create the RAGAS LLM using the selected evaluation model.
    _ragas_llm = llm_factory(
        eval_model,
        client=_ragas_client,
    )

    # Create the embedding model used by RAGAS.
    # The model is fixed so evaluation stays consistent across runs.
    _ragas_embedding = embedding_factory(
        "openai",
        model=FIXED_EMBED_MODEL,
        client=_ragas_client,
    )


async def scoring_metric(user_input, retrieved_contexts, response):
    """
    Calculate RAGAS scores for a generated response.

    This function evaluates the response using four metrics:
    - Answer Relevancy
    - Faithfulness
    - Context Relevance
    - Response Groundedness

    Some metrics need retrieved contexts, while Answer Relevancy can run
    with only the user question and generated response.

    Args:
        user_input: The original user question.
        retrieved_contexts: The retrieved text chunks used to generate the answer.
        response: The generated answer text.

    Returns:
        A dictionary containing the metric scores.
        If a metric fails or cannot be calculated, its value stays as None.
    """

    # Default result structure.
    # Scores remain None when a metric fails or cannot be calculated.
    results = {
        "Answer Relevancy": None,
        "Faithfulness": None,
        "Context Relevance": None,
        "Response Groundedness": None,
    }

    # If no contexts are provided, use an empty list to avoid errors later.
    if retrieved_contexts is None:
        retrieved_contexts = []

    # Limit the number and size of contexts passed to RAGAS.
    # This helps avoid long prompts, high cost, slow evaluation, or model limits.
    MAX_RAGAS_CONTEXTS = 3
    MAX_RAGAS_CONTEXT_CHARS = 1500

    # Clean retrieved contexts by removing None values and empty text.
    cleaned_contexts = [
        str(ctx).strip()
        for ctx in retrieved_contexts
        if ctx is not None and str(ctx).strip()
    ]

    # Keep only the first few contexts and trim each one to the maximum length.
    retrieved_contexts = [
        ctx[:MAX_RAGAS_CONTEXT_CHARS]
        for ctx in cleaned_contexts[:MAX_RAGAS_CONTEXTS]
    ]

    # If the question or response is missing, no scoring can be performed.
    if not user_input or not response:
        return results

    # Limit the response length before sending it to RAGAS.
    # This keeps evaluation more stable and reduces the risk of model-limit errors.
    MAX_RAGAS_RESPONSE_CHARS = 4000
    response = response[:MAX_RAGAS_RESPONSE_CHARS]

    # Make sure init_ragas() has been called before scoring.
    if _ragas_llm is None:
        print("RAGAS LLM is not initialised. Did you call init_ragas()?")

        # Return empty scores if the evaluator LLM is not ready.
        return results

    # 1. Answer Relevancy
    # This checks whether the response is relevant to the user question.
    try:
        # Create the Answer Relevancy scorer.
        # This metric needs both an LLM and embeddings.
        answer_relevancy_scorer = AnswerRelevancy(
            llm=_ragas_llm,
            embeddings=_ragas_embedding,
        )

        # Run the scorer asynchronously.
        answer_relevancy_result = await answer_relevancy_scorer.ascore(
            user_input=user_input,
            response=response,
        )

        # Store the numeric score.
        results["Answer Relevancy"] = answer_relevancy_result.value

    except Exception as e:
        # Keep the score as None if the metric fails.
        print(f"Answer Relevancy failed: {e}")

    # The remaining RAGAS metrics need retrieved contexts.
    # If no contexts are available, skip them and return the current results.
    if not retrieved_contexts:
        print("No retrieved contexts available. Skipping context-based RAGAS metrics.")
        return results

    # 2. Faithfulness
    # This checks whether the response is supported by the retrieved contexts.
    try:
        # Create the Faithfulness scorer.
        faithfulness_scorer = Faithfulness(llm=_ragas_llm)

        # Run the scorer using the question, response, and retrieved contexts.
        faithfulness_result = await faithfulness_scorer.ascore(
            user_input=user_input,
            response=response,
            retrieved_contexts=retrieved_contexts,
        )

        # Store the numeric score.
        results["Faithfulness"] = faithfulness_result.value

    except Exception as e:
        # Print extra debugging information because Faithfulness can fail
        # when contexts are too long, empty, or not suitable for evaluation.
        print("Faithfulness failed")
        print(f"Question: {user_input[:300]}")
        print(f"Response length: {len(response) if response else 0}")
        print(f"Number of contexts: {len(retrieved_contexts)}")
        print(
            "First context preview: "
            f"{retrieved_contexts[0][:500] if retrieved_contexts else 'NO CONTEXT'}"
        )
        print(f"Error: {repr(e)}")

    # 3. Context Relevance
    # This checks whether the retrieved contexts are relevant to the user question.
    try:
        # Create the Context Relevance scorer.
        context_relevance_scorer = ContextRelevance(llm=_ragas_llm)

        # Run the scorer using the question and retrieved contexts.
        context_relevance_result = await context_relevance_scorer.ascore(
            user_input=user_input,
            retrieved_contexts=retrieved_contexts,
        )

        # Store the numeric score.
        results["Context Relevance"] = context_relevance_result.value

    except Exception as e:
        # Keep the score as None if the metric fails.
        print(f"Context Relevance failed: {e}")

    # 4. Response Groundedness
    # This checks whether the generated response is grounded in the retrieved contexts.
    try:
        # Create the Response Groundedness scorer.
        response_groundedness_scorer = ResponseGroundedness(llm=_ragas_llm)

        # Run the scorer using the response and retrieved contexts.
        response_groundedness_result = await response_groundedness_scorer.ascore(
            response=response,
            retrieved_contexts=retrieved_contexts,
        )

        # Store the numeric score.
        results["Response Groundedness"] = response_groundedness_result.value

    except Exception as e:
        # Keep the score as None if the metric fails.
        print(f"Response Groundedness failed: {e}")

    # Return all available scores.
    return results