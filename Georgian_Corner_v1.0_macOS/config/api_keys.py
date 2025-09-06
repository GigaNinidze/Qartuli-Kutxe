"""API key storage and validation utilities."""
from __future__ import annotations

import os
from typing import Optional

from openai import OpenAI

from . import settings

_SECTION = "openai"
_KEY = "api_key"


def save_api_key(key: str) -> None:
    """Persist the OpenAI API key to the settings file."""
    settings.write_settings({_KEY: key}, section=_SECTION)


def load_api_key() -> Optional[str]:
    """Return the stored OpenAI API key or environment variable value if present."""
    # Prefer environment variable for forward-compatibility with headless use
    env_key = os.getenv("OPENAI_API_KEY")
    if env_key:
        return env_key
    config = settings.read_settings(section=_SECTION)
    return config.get(_KEY)


def validate_api_key(key: str) -> bool:
    """Check if the provided OpenAI key is valid by making a lightweight request."""
    try:
        # NOTE: Listing models is an inexpensive way to test the key.
        client = OpenAI(api_key=key)
        _ = client.models.list()
        return True
    except Exception:  # pylint: disable=broad-except
        return False
