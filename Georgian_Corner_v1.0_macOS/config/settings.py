"""Configuration management utilities.
Responsible for locating the user configuration directory and reading/writing
application-specific settings such as window size, last used tone, etc.
"""

from __future__ import annotations

import configparser
import os
from pathlib import Path
from typing import Any, Dict

APP_NAME = "ქართული კუთხე"
CONFIG_FILE_NAME = "settings.ini"
DEFAULT_SECTION = "general"


def _get_config_dir() -> Path:
    """Return OS-appropriate configuration directory (~/.config/<APP_NAME>)."""
    # Respect XDG spec on Unix-like systems and fall back to ~/.config
    xdg_config_home = os.environ.get("XDG_CONFIG_HOME")
    if xdg_config_home:
        base = Path(xdg_config_home)
    else:
        base = Path.home() / ".config"
    cfg_dir = base / APP_NAME
    cfg_dir.mkdir(parents=True, exist_ok=True)
    return cfg_dir


def _get_config_path() -> Path:
    return _get_config_dir() / CONFIG_FILE_NAME


def read_settings(section: str = DEFAULT_SECTION) -> Dict[str, str]:
    """Read settings from the given section.

    Returns an empty dict if no settings exist yet.
    """
    cfg_path = _get_config_path()
    parser = configparser.ConfigParser()
    if cfg_path.exists():
        parser.read(cfg_path)
    return dict(parser[section]) if parser.has_section(section) else {}


def write_settings(data: Dict[str, Any], section: str = DEFAULT_SECTION) -> None:
    """Persist provided key/value pairs to the configuration file."""
    cfg_path = _get_config_path()
    parser = configparser.ConfigParser()
    if cfg_path.exists():
        parser.read(cfg_path)

    if not parser.has_section(section):
        parser.add_section(section)

    for key, value in data.items():
        parser.set(section, key, str(value))

    with cfg_path.open("w") as fp:
        parser.write(fp)
