# config.py

# Import Path to create and manage file/folder paths safely.
from pathlib import Path


# Base URL for the OpenRouter API.
# OpenRouter provides access to multiple LLM providers through one API endpoint.
OPENROUTER_API_BASE = "https://openrouter.ai/api/v1"


# List of LLMs available in the app sidebar.
# The user can select one of these models at query time.
OPENROUTER_MODELS = [
    "google/gemini-2.0-flash-001",
    "anthropic/claude-sonnet-4",
    "google/gemini-2.5-pro",
    "openai/gpt-5.5-pro",
    "openai/gpt-4o-mini",
    "openai/gpt-4o",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3.7-sonnet",
    "meta-llama/llama-3.3-70b-instruct",
]


# The LLM model that was used when building the fixed property graph index.
# This value is shown in the app so users know which model created the index.
FIXED_INDEX_LLM_MODEL = "openai/gpt-4o-mini"


# The embedding model used when building the fixed index.
# The same embedding model should also be used when loading/querying the index
# to keep retrieval behaviour consistent.
FIXED_EMBED_MODEL = "text-embedding-3-small"


# Folder path where the fixed property graph index is stored.
# This index is loaded by the app instead of being rebuilt each time.
FIXED_INDEX_DIR = Path(
    "./storage_property_graph/openai_gpt-4o-mini__text-embedding-3-small"
)


# Files that must exist inside the fixed index folder.
# The app checks for these files before loading the index.
# If one or more files are missing, the index is treated as incomplete.
REQUIRED_INDEX_FILES = [
    "docstore.json",
    "index_store.json",
    "graph_store.json",
    "property_graph_store.json",
]


# Folder where combined output CSV files from batch runs are saved.
COMBINED_DIR = Path("saved_runs") / "_combined"


# Create the combined output folder if it does not already exist.
# parents=True creates any missing parent folders.
# exist_ok=True prevents an error if the folder already exists.
COMBINED_DIR.mkdir(parents=True, exist_ok=True)


# Name of the folder used to store graph PNG screenshots.
# This folder is created inside each batch run folder when graph screenshots are saved.
GRAPH_SCREENSHOTS_DIRNAME = "graph_screenshots"


# Colour palette used for graph visualisation.
# These colours are assigned to graph nodes in the graph service.
PALETTE = [
    "#534AB7",
    "#0F6E56",
    "#993C1D",
    "#854F0B",
    "#185FA5",
    "#3B6D11",
    "#72243E",
    "#444441",
    "#0C447C",
    "#712B13",
]