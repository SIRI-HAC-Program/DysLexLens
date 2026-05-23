# services/index_service.py

# Import Streamlit to use caching and show a loading spinner in the app.
import streamlit as st

# Import LlamaIndex settings and storage tools.
# Settings stores the active LLM and embedding model for LlamaIndex.
# StorageContext is used to load an index from a saved folder.
# load_index_from_storage loads the persisted index files.
from llama_index.core import Settings, StorageContext, load_index_from_storage

# Import the expected index type for type hinting.
from llama_index.core import PropertyGraphIndex

# Import fixed index settings from the project configuration.
# FIXED_INDEX_DIR is the folder where the saved index is stored.
# REQUIRED_INDEX_FILES lists the files that must exist for the index to be valid.
from config import FIXED_INDEX_DIR, REQUIRED_INDEX_FILES

# Import helper functions for creating the LLM and embedding model.
from services.llm_service import make_llm, make_embed_model

# Import helper function that checks whether the saved index folder has real index files.
from utils.file_utils import has_real_index_files


@st.cache_resource(show_spinner="Loading fixed property graph index...")
def load_fixed_index(api_key: str, query_model: str) -> PropertyGraphIndex:
    """
    Load the fixed property graph index from local storage.

    This function:
    - Checks whether the fixed index folder contains the required files.
    - Sets the LLM used for querying.
    - Sets the embedding model used by LlamaIndex.
    - Loads the saved index from disk.
    - Caches the loaded index in Streamlit so it is not reloaded every time.

    Args:
        api_key: The API key used to initialise the LLM and embedding model.
        query_model: The LLM model name used for querying the fixed index.

    Returns:
        The loaded PropertyGraphIndex.

    Raises:
        FileNotFoundError: If the fixed index folder is missing required files.
    """

    # Check whether the fixed index folder contains valid saved index files.
    # This prevents the app from trying to load an incomplete or missing index.
    if not has_real_index_files(FIXED_INDEX_DIR):

        # Identify which required files are missing from the index folder.
        missing = [
            f
            for f in REQUIRED_INDEX_FILES
            if not (FIXED_INDEX_DIR / f).exists()
        ]

        # Stop the process with a clear error message.
        # This makes debugging easier when the index folder is incomplete.
        raise FileNotFoundError(
            f"Existing fixed index folder is incomplete.\n"
            f"Expected folder: {FIXED_INDEX_DIR}\n"
            f"Missing files: {missing}"
        )

    # Set the LLM that LlamaIndex will use for querying.
    # This uses the selected query model and the provided API key.
    Settings.llm = make_llm(query_model, api_key)

    # Set the embedding model used by LlamaIndex.
    # This should match the embedding model used when the index was created.
    Settings.embed_model = make_embed_model(api_key)

    # Create a storage context that points to the fixed saved index folder.
    storage_context = StorageContext.from_defaults(
        persist_dir=str(FIXED_INDEX_DIR)
    )

    # Load the index from the saved storage context.
    index = load_index_from_storage(storage_context)

    # Return the loaded index so other services can use it for retrieval and querying.
    return index