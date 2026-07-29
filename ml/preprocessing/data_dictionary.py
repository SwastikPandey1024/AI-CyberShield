"""
Data Dictionary

Provides metadata, descriptions, and mappings for dataset features and attack labels.

This module serves as the single source of truth for:
- Feature name mappings (raw → canonical)
- Feature descriptions and data types
- Attack label encodings (categorical ↔ numerical)
- Feature categories (traffic stats, timestamps, flags, etc.)

WHY CONFIG-DRIVEN:
    Feature definitions and label mappings are loaded from YAML files in
    ``configs/datasets/cicids2017/`` at import time rather than being hardcoded
    as Python dict literals. This means a future dataset like UNSW-NB15
    only requires a new YAML file — no Python code changes are needed.

    The typed access layer (FeatureMetadata, AttackCategory, lookup functions)
    remains in Python so callers get IDE autocompletion and type safety.
    The data itself lives in YAML so it can be edited, reviewed, and versioned
    independently of the code.

Module-level constants:
    CICIDS2017_FEATURES
    CICIDS2017_LABEL_MAPPING
    CATEGORY_TO_INDEX

    These are populated at import time by the YAML loaders. Any code that
    imports these names continues to work unchanged.

TODO:
    - [DONE] Load feature definitions from an external YAML/JSON config for runtime extensibility.
    - Add versioning support for feature schemas across dataset versions.
    - Add statistical summaries (mean, std, min, max) for each feature as reference.
    - Add SHAP reference values for model explainability integration.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

import yaml

from ml.preprocessing.column_normalizer import ColumnNormalizer


# ──────────────────────────────────────────────
# Default YAML paths
# ──────────────────────────────────────────────

_PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FEATURES_PATH: Path = _PROJECT_ROOT / "configs" / "datasets" / "cicids2017" / "features.yaml"
DEFAULT_LABEL_MAPPING_PATH: Path = _PROJECT_ROOT / "configs" / "datasets" / "cicids2017" / "attack_mapping.yaml"


# ──────────────────────────────────────────────
# Core Types
# ──────────────────────────────────────────────


class AttackCategory(Enum):
    """
    Enumeration of known attack categories in the CICIDS2017 dataset.

    These map to the canonical attack labels used across the pipeline.
    The ``unknown`` category is reserved for unlabelled or out-of-distribution samples.

    TODO: Expand for multi-dataset support (UNSW-NB15, CSE-CIC-IDS2018).
    """

    BENIGN = "BENIGN"
    DOS = "DoS"
    DDOS = "DDoS"
    PORT_SCAN = "PortScan"
    BRUTE_FORCE = "BruteForce"
    WEB_ATTACK = "WebAttack"
    BOTNET = "Botnet"
    INFILTRATION = "Infiltration"
    UNKNOWN = "Unknown"


@dataclass
class FeatureMetadata:
    """
    Metadata describing a single feature (column) in the dataset.

    Attributes:
        raw_name: Original column name from the source dataset.
        canonical_name: Clean, standardised name used across the pipeline.
        dtype: Expected pandas/numpy data type string (e.g. 'float64', 'int64', 'object').
        description: Human-readable description of what this feature represents.
        category: Feature category (e.g. 'flow', 'time', 'flag', 'payload').
        is_target: Whether this column is the target/label.
        is_temporal: Whether this feature has a time-series component.
        min_value: Expected minimum value (if known).
        max_value: Expected maximum value (if known).
        enum_values: If categorical, the set of allowed values.
    """

    raw_name: str
    canonical_name: str
    dtype: str
    description: str
    category: str = "unknown"
    is_target: bool = False
    is_temporal: bool = False
    min_value: float | None = None
    max_value: float | None = None
    enum_values: list[str] | None = None


# ──────────────────────────────────────────────
# YAML Loaders
# ──────────────────────────────────────────────





def _build_category_mapping(
    raw_name: str,
    known_categories: dict[str, str],
) -> str:
    """
    Map a raw feature-type name to the closest known category.

    Falls back to "unknown" if no match is found.
    """
    lower = raw_name.strip().lower()
    for alias, canonical in known_categories.items():
        if alias.lower() == lower:
            return canonical
    return "unknown"


_CATEGORY_ALIASES: dict[str, str] = {
    "flow": "flow",
    "time": "time",
    "flag": "flag",
    "payload": "payload",
    "subflow": "subflow",
    "idle": "idle",
    "label": "label",
}


def load_feature_catalogue(
    path: Path = DEFAULT_FEATURES_PATH,
) -> list[FeatureMetadata]:
    """
    Load and validate feature metadata from YAML into ``FeatureMetadata`` objects.

    Args:
        path: Path to the ``features.yaml`` config file.

    Returns:
        List of ``FeatureMetadata`` objects.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        yaml.YAMLError: If the YAML is malformed.

    TODO:
        - Add schema validation with a JSON Schema / Pydantic model.
        - Support loading multiple dataset configs from a registry.
    """
    with open(path, "r", encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh)

    features_raw: list[dict[str, Any]] = raw.get("features", [])
    features: list[FeatureMetadata] = []

    for entry in features_raw:
        raw_name: str = entry["name"]
        canonical: str = ColumnNormalizer.to_canonical_name(raw_name)
        category: str = _build_category_mapping(
            entry.get("feature_type", "unknown"),
            _CATEGORY_ALIASES,
        )
        is_target: bool = entry.get("is_target", False)

        features.append(
            FeatureMetadata(
                raw_name=raw_name,
                canonical_name=canonical,
                dtype=entry["dtype"],
                description=entry["description"],
                category=category,
                is_target=is_target,
            )
        )

    return features


def load_label_mapping(
    path: Path = DEFAULT_LABEL_MAPPING_PATH,
) -> dict[str, AttackCategory]:
    """
    Load the label-to-category mapping from YAML.

    Args:
        path: Path to the ``attack_mapping.yaml`` config file.

    Returns:
        Dict mapping raw label strings to ``AttackCategory`` enum values.

    Raises:
        FileNotFoundError: If the YAML file does not exist.
        yaml.YAMLError: If the YAML is malformed.
    """
    with open(path, "r", encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh)

    label_data: dict[str, str] = raw.get("label_to_category", {})
    mapping: dict[str, AttackCategory] = {}

    for raw_label, cat_name in label_data.items():
        try:
            mapping[raw_label] = AttackCategory(cat_name)
        except ValueError:
            mapping[raw_label] = AttackCategory.UNKNOWN

    return mapping


def load_category_to_index(
    path: Path = DEFAULT_LABEL_MAPPING_PATH,
) -> dict[str, int]:
    """
    Load the category-to-integer-index mapping from YAML.

    Args:
        path: Path to the ``attack_mapping.yaml`` config file.

    Returns:
        Dict mapping canonical category names to integer indices.
    """
    with open(path, "r", encoding="utf-8") as fh:
        raw: dict[str, Any] = yaml.safe_load(fh)

    index_data: dict[str, int] = raw.get("category_to_index", {})
    return index_data


# ──────────────────────────────────────────────
# Module-Level Constants (populated at import time)
# ──────────────────────────────────────────────

#: List of ``FeatureMetadata`` for the CICIDS2017 dataset.
#: Loaded from ``configs/datasets/cicids2017/features.yaml``.
CICIDS2017_FEATURES: list[FeatureMetadata] = load_feature_catalogue()

#: Mapping of raw CICIDS2017 Label column values to canonical ``AttackCategory`` enum.
#: Loaded from ``configs/datasets/cicids2017/attack_mapping.yaml``.
CICIDS2017_LABEL_MAPPING: dict[str, AttackCategory] = load_label_mapping()

#: Mapping of canonical category names to integer indices for model training.
#: Loaded from ``configs/datasets/cicids2017/attack_mapping.yaml``.
CATEGORY_TO_INDEX: dict[str, int] = load_category_to_index()


# ──────────────────────────────────────────────
# Lookup & Helper Functions
# ──────────────────────────────────────────────


def normalize_raw_label(raw_label: str) -> str:
    """
    Normalise a raw label string before YAML key lookup.

    CICIDS2017 Web Attack labels contain U+FFFD (the Unicode Replacement
    Character, 0xef 0xbf 0xbd) as a separator — confirmed by binary read on
    2026-07-29. Stripping U+FFFD and collapsing the resulting double-space
    produces ``'Web Attack Brute Force'`` which matches the YAML key.

    This is the only place in the pipeline that applies label normalisation.
    All other modules call ``encode_label`` which invokes this automatically.

    Args:
        raw_label: The raw label string as read from the dataset.

    Returns:
        Normalised label string ready for YAML key lookup.
    """
    import re
    # Strip U+FFFD (binary artefact in CICIDS2017 Web Attack labels)
    normalised = raw_label.replace("\ufffd", "")
    # Collapse multiple consecutive spaces produced by stripping
    normalised = re.sub(r"  +", " ", normalised)
    return normalised.strip()


def encode_label(raw_label: str) -> AttackCategory:
    """
    Map a raw label string from the dataset to a canonical ``AttackCategory``.

    Applies ``normalize_raw_label`` before lookup to handle known encoding
    artefacts in CICIDS2017 (U+FFFD separator in Web Attack labels).

    Args:
        raw_label: The label string from the dataset (e.g. ``'DoS Hulk'``).

    Returns:
        Corresponding ``AttackCategory`` enum value.
        Returns ``AttackCategory.UNKNOWN`` if the label is not recognised.
    """
    normalised = normalize_raw_label(raw_label)
    return CICIDS2017_LABEL_MAPPING.get(normalised, AttackCategory.UNKNOWN)


def encode_label_to_int(raw_label: str) -> int:
    """
    Map a raw label string to an integer encoding for model training.

    Args:
        raw_label: The label string from the dataset.

    Returns:
        Integer encoding starting from 0 (BENIGN=0).

    TODO:
        - Support custom encoding schemes via configuration.
        - Implement inverse transform (int to label name).
    """
    category = encode_label(raw_label)
    return list(AttackCategory).index(category)


def get_feature_by_raw_name(raw_name: str) -> FeatureMetadata | None:
    """
    Look up feature metadata by its raw column name from the source dataset.

    Args:
        raw_name: The column name as it appears in the raw CSV.

    Returns:
        ``FeatureMetadata`` if found, ``None`` otherwise.

    TODO:
        - Add partial/fuzzy matching for column name variations.
    """
    for feature in CICIDS2017_FEATURES:
        if feature.raw_name == raw_name:
            return feature
    return None


def get_feature_by_canonical_name(canonical_name: str) -> FeatureMetadata | None:
    """
    Look up feature metadata by its canonical (pipeline) name.

    Args:
        canonical_name: The standardised feature name used internally.

    Returns:
        ``FeatureMetadata`` if found, ``None`` otherwise.
    """
    for feature in CICIDS2017_FEATURES:
        if feature.canonical_name == canonical_name:
            return feature
    return None


def get_feature_names_by_category(category: str) -> list[str]:
    """
    Get all canonical feature names belonging to a given category.

    Args:
        category: Feature category (e.g. 'flow', 'time', 'flag').

    Returns:
        List of canonical feature names in that category.
    """
    return [
        f.canonical_name
        for f in CICIDS2017_FEATURES
        if f.category == category and not f.is_target
    ]


def get_all_feature_names(exclude_target: bool = True) -> list[str]:
    """
    Get all canonical feature names from the data dictionary.

    Args:
        exclude_target: If True, excludes the target/label column.

    Returns:
        List of canonical feature names.
    """
    if exclude_target:
        return [f.canonical_name for f in CICIDS2017_FEATURES if not f.is_target]
    return [f.canonical_name for f in CICIDS2017_FEATURES]


def get_raw_to_canonical_mapping() -> dict[str, str]:
    """
    Build a mapping dictionary from raw column names to canonical names.

    Returns:
        Dict mapping raw_name to canonical_name.
    """
    return {f.raw_name: f.canonical_name for f in CICIDS2017_FEATURES}


def get_canonical_to_raw_mapping() -> dict[str, str]:
    """
    Build a mapping dictionary from canonical names to raw column names.

    Returns:
        Dict mapping canonical_name to raw_name.
    """
    return {f.canonical_name: f.raw_name for f in CICIDS2017_FEATURES}


def get_attack_label_distribution() -> dict[str, list[str]]:
    """
    Get the expected distribution of raw labels grouped by canonical attack category.

    Returns:
        Dict mapping canonical AttackCategory name to list of raw labels.
    """
    distribution: dict[str, list[str]] = {}
    for raw_label, category in CICIDS2017_LABEL_MAPPING.items():
        cat_name = category.value
        if cat_name not in distribution:
            distribution[cat_name] = []
        distribution[cat_name].append(raw_label)
    return distribution
