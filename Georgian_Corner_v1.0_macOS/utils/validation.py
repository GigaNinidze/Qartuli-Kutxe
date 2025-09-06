"""Validation helpers for spreadsheet rows."""

__all__ = ["row_is_complete"]


def row_is_complete(name: str, description: str) -> bool:
    """Return True if both name and description are non-empty strings."""
    return bool(str(name).strip()) and bool(str(description).strip())
