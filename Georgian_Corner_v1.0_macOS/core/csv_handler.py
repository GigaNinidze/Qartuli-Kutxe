"""CSV import/export helpers for Tako Georgian Ads Generator.

The expected CSV structure is three columns in the following order:
1. Product name (A)
2. Product description (B)
3. Generated advertisement (C)

The headers are optional. If no header row exists, the first row of data will
still be read correctly. Internally we normalise the DataFrame to always carry
the canonical column names: ``name``, ``description``, ``ad``.
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

__all__ = ["import_csv", "export_csv"]

_CANONICAL_COLUMNS = ["name", "description", "ad"]


def _normalise_dataframe(df: pd.DataFrame) -> pd.DataFrame:
     """Ensure DataFrame has the canonical columns in the correct order."""
     # If the CSV contained headers that already match in any order, rename them.
     mapping: dict[str, str] = {}
     for original in df.columns:
         normalised = str(original).lower().strip()
         if normalised in ("name", "product name", "სახელი", "პროდუქტის სახელი"):
             mapping[original] = "name"
         elif normalised in ("description", "product description", "აღწერა"):
             mapping[original] = "description"
         elif normalised in ("ad", "advertisement", "generated advertisement", "რეკლამა"):
             mapping[original] = "ad"

     if mapping:
         df = df.rename(columns=mapping)

     # In case header row was missing, treat current columns as data and relabel.
     if len(df.columns) < 3 or not set(_CANONICAL_COLUMNS).issubset(df.columns):
         # Assume the CSV had no header row
         df.columns = _CANONICAL_COLUMNS[: len(df.columns)]

     # Ensure all three expected columns exist
     for col in _CANONICAL_COLUMNS:
         if col not in df.columns:
             df[col] = ""

     return df[_CANONICAL_COLUMNS]


def import_csv(path: str | Path) -> pd.DataFrame:
     """Read CSV file and return normalised DataFrame."""
     path = Path(path)
     if not path.exists():
         raise FileNotFoundError(path)

     try:
         # Try reading with header first.
         df = pd.read_csv(path)
     except pd.errors.ParserError:
         # Fallback: read without header
         df = pd.read_csv(path, header=None)

     return _normalise_dataframe(df)


def export_csv(df: pd.DataFrame, path: str | Path) -> None:
     """Write DataFrame to CSV using UTF-8 encoding."""
     path = Path(path)
     df.to_csv(path, index=False, encoding="utf-8-sig", header=True)
