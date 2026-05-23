# utils/file_utils.py
import re
from pathlib import Path
from typing import Optional

import pandas as pd

from config import REQUIRED_INDEX_FILES


# -------------------------------------------------
# Safe file / folder naming
# -------------------------------------------------

def safe_model_dir_name(name: str) -> str:
    """
    Convert a model or arbitrary string into a filesystem-safe name.
    """
    return re.sub(r"[^a-zA-Z0-9._-]+", "_", str(name))


def safe_file_stem(name: str, max_len: int = 120) -> str:
    """
    Create a safe filename stem with a max length.
    """
    cleaned = safe_model_dir_name(name)
    return cleaned[:max_len] if cleaned else "item"


# -------------------------------------------------
# Fixed index existence checks
# -------------------------------------------------

def has_real_index_files(persist_dir: Path) -> bool:
    """
    Check whether the fixed index directory exists
    and contains all required index files.
    """
    return persist_dir.exists() and all((persist_dir / f).exists() for f in REQUIRED_INDEX_FILES)


# -------------------------------------------------
# CSV helpers
# -------------------------------------------------

def append_rows_to_csv(csv_path: Path, rows: list[dict]):
    """
    Append rows to a CSV file, creating it if needed.
    Drops duplicate rows after concatenation.
    """
    if not rows:
        return

    df_new = pd.DataFrame(rows)

    if csv_path.exists():
        try:
            df_old = pd.read_csv(csv_path)
            df_all = pd.concat([df_old, df_new], ignore_index=True)
        except Exception:
            df_all = df_new
    else:
        df_all = df_new

    df_all = df_all.drop_duplicates()
    csv_path.parent.mkdir(parents=True, exist_ok=True)
    df_all.to_csv(csv_path, index=False)


def bytes_from_df(df: pd.DataFrame) -> bytes:
    """
    Convert a dataframe to UTF-8 CSV bytes for Streamlit downloads.
    """
    return df.to_csv(index=False).encode("utf-8")


# -------------------------------------------------
# Delimited file loading
# -------------------------------------------------

def load_delimited_upload(uploaded_file) -> pd.DataFrame:
    """
    Load a CSV/TSV/TXT uploaded via Streamlit file_uploader,
    trying multiple encodings and delimiters.
    """
    if uploaded_file is None:
        return pd.DataFrame()

    raw = uploaded_file.getvalue()

    encodings_to_try = [
        "utf-8",
        "utf-8-sig",
        "cp1252",
        "latin1",
        "utf-16",
        "utf-16-le",
        "utf-16-be",
    ]

    last_error: Optional[Exception] = None

    for enc in encodings_to_try:
        try:
            text = raw.decode(enc)

            # First try delimiter auto-detection
            try:
                df = pd.read_csv(pd.io.common.StringIO(text), sep=None, engine="python")
                if not df.empty or len(df.columns) > 1:
                    return df
            except Exception:
                pass

            # Then try common separators explicitly
            for sep in [",", "\t", ";"]:
                try:
                    df = pd.read_csv(pd.io.common.StringIO(text), sep=sep)
                    if not df.empty or len(df.columns) > 1:
                        return df
                except Exception:
                    continue

        except Exception as e:
            last_error = e

    raise ValueError(
        f"Could not read uploaded file with common encodings/delimiters. "
        f"Last error: {last_error}"
    )


def load_question_csv_from_upload(uploaded_file) -> pd.DataFrame:
    """
    Wrapper for loading the uploaded research question file.
    """
    return load_delimited_upload(uploaded_file)

def validate_question_df(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    """
    Validate the uploaded research-question dataframe.

    Required:
    - research_question column

    Optional:
    - question_id column (auto-generated if missing)
    - followup_* columns
    """
    if df.empty:
        raise ValueError("The uploaded question CSV is empty.")

    df.columns = [str(c).strip() for c in df.columns]

    if "research_question" not in df.columns:
        raise ValueError("Question CSV must contain a 'research_question' column.")

    if "question_id" not in df.columns:
        df.insert(0, "question_id", [f"RQ{i+1}" for i in range(len(df))])

    followup_cols = [c for c in df.columns if c.lower().startswith("followup")]
    return df, followup_cols
