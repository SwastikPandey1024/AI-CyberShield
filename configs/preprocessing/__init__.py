"""AI CyberShield — Preprocessing Configuration Package.

Configuration files for data cleaning, feature selection, and scaling strategies.

Enables runtime extensibility: new preprocessing strategies can be added by
creating new YAML config files without modifying Python code.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


_CONFIG_DIR = Path(__file__).resolve().parent


def load_config(name: str) -> dict[str, Any]:
    """Load a preprocessing configuration from a YAML file.

    Args:
        name: Configuration name (without .yaml extension),
              e.g. 'cleaning', 'feature_selection', 'scaling'.

    Returns:
        Dict containing the parsed YAML configuration.

    Raises:
        FileNotFoundError: If the config file does not exist.
        yaml.YAMLError: If the YAML is malformed.

    Example:
        >>> cleaning_cfg = load_config('cleaning')
        >>> cleaning_cfg['missing_values']['strategy']
        'drop'
    """
    path = _CONFIG_DIR / f"{name}.yaml"
    with open(path, "r", encoding="utf-8") as fh:
        return dict(yaml.safe_load(fh))
