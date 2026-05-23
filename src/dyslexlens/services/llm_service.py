# services/llm_service.py

# Import the OpenAI-compatible LLM wrapper from LlamaIndex.
# This is used because OpenRouter follows an OpenAI-like API format.
from llama_index.llms.openai_like import OpenAILike

# Import the OpenAI embedding model wrapper from LlamaIndex.
# This is used to create vector embeddings for retrieval.
from llama_index.embeddings.openai import OpenAIEmbedding

# Import project configuration values.
# OPENROUTER_API_BASE stores the OpenRouter API endpoint.
# FIXED_EMBED_MODEL stores the embedding model used by the fixed index.
from config import OPENROUTER_API_BASE, FIXED_EMBED_MODEL


def make_llm(model_name: str, api_key: str) -> OpenAILike:
    """
    Create and return an OpenAI-compatible LLM instance.

    This function is used to initialise the query-time language model.
    The model is accessed through OpenRouter using an OpenAI-like API.

    Args:
        model_name: The name of the LLM selected for querying.
        api_key: The OpenRouter API key.

    Returns:
        An OpenAILike LLM object configured for chat-based responses.
    """

    # Create the LLM object using the selected model and OpenRouter API settings.
    return OpenAILike(
        # The model used for answering questions.
        model=model_name,

        # The OpenRouter base URL used to send API requests.
        api_base=OPENROUTER_API_BASE,

        # The user's OpenRouter API key.
        api_key=api_key,

        # This tells LlamaIndex that the model works as a chat model.
        is_chat_model=True,

        # This enables function-calling support when the model provides it.
        is_function_calling_model=True,

        # Maximum context size supported for long prompts and retrieved context.
        context_window=128000,

        # Low temperature makes responses more stable and less random.
        temperature=0.1,
    )


def make_embed_model(api_key: str) -> OpenAIEmbedding:
    """
    Create and return the embedding model used for retrieval.

    This function should use the same embedding model that was used
    when the fixed index was created. This helps keep retrieval behaviour
    consistent between indexing and querying.

    Args:
        api_key: The OpenRouter API key.

    Returns:
        An OpenAIEmbedding object configured with the fixed embedding model.
    """

    # Create the embedding model using the fixed embedding model name.
    return OpenAIEmbedding(
        # The embedding model used by the project.
        model=FIXED_EMBED_MODEL,

        # The user's OpenRouter API key.
        api_key=api_key,

        # The OpenRouter base URL used for embedding API requests.
        api_base=OPENROUTER_API_BASE,
    )