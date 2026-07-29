"""
Preprocessing Pipeline
======================

Evidence-driven preprocessing for the CICIDS2017 dataset.
Every decision in this module is backed by EDA findings in
``reports/data/eda/findings.md`` (Phase 2.5, 2026-07-29).

Design decisions (from EDA evidence):
  - Drop 8 fully-constant columns (6 bulk + 2 flag) — zero variance across all 8 files
  - Drop 7 confirmed exact-duplicate columns (r=1.0, CICFlowMeter definition)
  - Replace Inf in Flow Bytes/s with NaN (100% co-occurs with Flow Duration==0)
  - Drop rows with remaining NaN (only Flow Bytes/s affected, 1,358 rows, 0.048%)
  - Drop duplicate rows (keep='first') — 9.06% overall, BENIGN-concentrated
  - Normalise raw label strings and encode to integer via attack_mapping.yaml
  - Stratified train/val/test split (required: 4 classes have <1000 samples)
  - RobustScaler (justification: Init_Win_bytes_* sentinel -1 values in 30-62%
    of rows make StandardScaler mean/std unreliable)
  - Save fitted scaler + label encoder alongside processed data

NOT done here (EDA-informed deferrals, require separate decisions):
  - Init_Win_bytes_* sentinel -1 treatment (kept as-is for now)
  - Class resampling (SMOTE / undersampling — modeling decision, not here)
  - Heartbleed/Infiltration class merging (modeling decision)
  - Correlation-based feature removal beyond confirmed exact duplicates
"""

from __future__ import annotations

import json
import logging
import pickle
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler

from ml.preprocessing.column_normalizer import ColumnNormalizer
from ml.preprocessing.data_dictionary import (
    CATEGORY_TO_INDEX,
    encode_label,
    normalize_raw_label,
)

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# EDA-derived constants (do NOT change without updating findings.md)
# ──────────────────────────────────────────────

#: Columns confirmed constant (unique_count <= 1) across ALL 8 CICIDS2017 files.
#: Source: EDA Step 1, 2026-07-29.
CONSTANT_COLUMNS: list[str] = [
    "Bwd Avg Bulk Rate",
    "Bwd Avg Bytes/Bulk",
    "Bwd Avg Packets/Bulk",
    "Fwd Avg Bulk Rate",
    "Fwd Avg Bytes/Bulk",
    "Fwd Avg Packets/Bulk",
    "Bwd PSH Flags",
    "Bwd URG Flags",
]

#: Columns confirmed exact duplicates (r=1.0000) from CICFlowMeter definition.
#: Each pair: keep the first column, drop the second.
#: Source: EDA Step 5, 2026-07-29 (Friday-DDos file, confirmed by CICFlowMeter docs).
DUPLICATE_COLUMNS: list[str] = [
    "Subflow Fwd Packets",      # = Total Fwd Packets
    "Subflow Bwd Packets",      # = Total Backward Packets
    "Subflow Fwd Bytes",        # = Total Length of Fwd Packets
    "Subflow Bwd Bytes",        # = Total Length of Bwd Packets
    "Avg Fwd Segment Size",     # = Fwd Packet Length Mean
    "Avg Bwd Segment Size",     # = Bwd Packet Length Mean
    "Fwd Header Length.1",      # = Fwd Header Length (CICFlowMeter duplicate column bug)
]

#: Target column name (post-ColumnNormalizer whitespace stripping).
TARGET_COLUMN = "Label"


# ──────────────────────────────────────────────
# Result dataclass
# ──────────────────────────────────────────────


@dataclass
class PreprocessingResult:
    """
    Output of the preprocessing pipeline: split DataFrames and metadata.

    Attributes:
        X_train: Training feature matrix.
        X_val:   Validation feature matrix.
        X_test:  Test feature matrix.
        y_train: Training label series (integer-encoded).
        y_val:   Validation label series.
        y_test:  Test label series.
        feature_names: List of feature column names (post-preprocessing).
        label_names:   Dict mapping integer index to category name string.
        scaler:        Fitted RobustScaler (fit on X_train only).
        stats:         Dict of preprocessing statistics for auditability.
    """

    X_train: pd.DataFrame
    X_val: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_val: pd.Series
    y_test: pd.Series
    feature_names: list[str]
    label_names: dict[int, str]
    scaler: RobustScaler
    stats: dict[str, Any]


# ──────────────────────────────────────────────
# Preprocessor
# ──────────────────────────────────────────────


class CICIDSPreprocessor:
    """
    Evidence-driven preprocessing pipeline for the CICIDS2017 dataset.

    Every transformation step is logged at INFO level with before/after counts
    so the pipeline is fully auditable without re-reading the source data.

    Args:
        test_size:  Fraction of data reserved for test split.
        val_size:   Fraction of (train+val) reserved for validation.
        random_state: Random seed for reproducibility.
    """

    def __init__(
        self,
        test_size: float = 0.20,
        val_size: float = 0.10,
        random_state: int = 42,
    ) -> None:
        self.test_size = test_size
        self.val_size = val_size
        self.random_state = random_state
        self._stats: dict[str, Any] = {}

    # ── public API ─────────────────────────────

    def fit_transform(
        self,
        csv_dir: Path,
        *,
        glob_pattern: str = "*.csv",
    ) -> PreprocessingResult:
        """
        Load, clean, encode, scale, and split the entire CICIDS2017 dataset.

        Args:
            csv_dir:      Directory containing the 8 raw CICIDS2017 CSV files.
            glob_pattern: Glob pattern to match CSV files (default ``*.csv``).

        Returns:
            ``PreprocessingResult`` containing all splits + fitted scaler.
        """
        # 1. Load all CSVs
        df = self._load_all(csv_dir, glob_pattern)

        # 2. Drop constant + duplicate columns
        df = self._drop_redundant_columns(df)

        # 3. Handle Infinity → NaN → drop NaN rows
        df = self._fix_infinity_and_nan(df)

        # 4. Drop duplicate rows
        df = self._drop_duplicates(df)

        # 5. Encode labels → integer
        y = self._encode_labels(df)
        X = df.drop(columns=[TARGET_COLUMN])

        # 6. Stratified train / val / test split
        X_train, X_val, X_test, y_train, y_val, y_test = self._split(X, y)

        # 7. Fit scaler on train, transform all splits
        scaler = RobustScaler()
        X_train_scaled = pd.DataFrame(
            scaler.fit_transform(X_train),
            columns=X_train.columns,
            index=X_train.index,
        )
        X_val_scaled = pd.DataFrame(
            scaler.transform(X_val),
            columns=X_val.columns,
            index=X_val.index,
        )
        X_test_scaled = pd.DataFrame(
            scaler.transform(X_test),
            columns=X_test.columns,
            index=X_test.index,
        )

        # 8. Build label names (int index → category string)
        label_names = {v: k for k, v in CATEGORY_TO_INDEX.items()}

        self._stats["split_sizes"] = {
            "train": len(X_train_scaled),
            "val": len(X_val_scaled),
            "test": len(X_test_scaled),
        }
        self._stats["n_features"] = len(X_train_scaled.columns)

        logger.info(
            "Preprocessing complete. train=%d  val=%d  test=%d  features=%d",
            len(X_train_scaled),
            len(X_val_scaled),
            len(X_test_scaled),
            len(X_train_scaled.columns),
        )

        return PreprocessingResult(
            X_train=X_train_scaled,
            X_val=X_val_scaled,
            X_test=X_test_scaled,
            y_train=y_train,
            y_val=y_val,
            y_test=y_test,
            feature_names=list(X_train_scaled.columns),
            label_names=label_names,
            scaler=scaler,
            stats=self._stats,
        )

    # ── private steps ───────────────────────────

    def _load_all(self, csv_dir: Path, glob_pattern: str) -> pd.DataFrame:
        """Load and concatenate all matching CSV files."""
        csv_files = sorted(csv_dir.glob(glob_pattern))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {csv_dir}")

        normalizer = ColumnNormalizer()
        frames: list[pd.DataFrame] = []

        for path in csv_files:
            logger.info("Loading %s ...", path.name)
            df = pd.read_csv(path, low_memory=False)
            df.columns = normalizer.normalize_columns(list(df.columns))
            frames.append(df)

        combined = pd.concat(frames, ignore_index=True)
        self._stats["raw_rows"] = len(combined)
        self._stats["raw_cols"] = len(combined.columns)
        self._stats["files_loaded"] = len(csv_files)
        logger.info(
            "Loaded %d files → %d rows × %d columns",
            len(csv_files),
            len(combined),
            len(combined.columns),
        )
        return combined

    def _drop_redundant_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop EDA-confirmed constant and exact-duplicate columns."""
        to_drop = [
            c for c in CONSTANT_COLUMNS + DUPLICATE_COLUMNS if c in df.columns
        ]
        df = df.drop(columns=to_drop)
        self._stats["dropped_constant"] = [c for c in CONSTANT_COLUMNS if c in to_drop]
        self._stats["dropped_duplicate"] = [c for c in DUPLICATE_COLUMNS if c in to_drop]
        logger.info(
            "Dropped %d redundant columns (%d constant + %d duplicate)",
            len(to_drop),
            len(self._stats["dropped_constant"]),
            len(self._stats["dropped_duplicate"]),
        )
        return df

    def _fix_infinity_and_nan(self, df: pd.DataFrame) -> pd.DataFrame:
        """Replace Inf → NaN, then drop rows with any NaN."""
        rows_before = len(df)
        # Replace all infinities with NaN
        inf_cols = []
        for col in df.select_dtypes(include=[np.number]).columns:
            inf_count = np.isinf(df[col]).sum()
            if inf_count > 0:
                df[col] = df[col].replace([np.inf, -np.inf], np.nan)
                inf_cols.append((col, int(inf_count)))

        self._stats["infinity_replaced"] = inf_cols

        # Drop rows with any remaining NaN
        df = df.dropna()
        rows_after = len(df)
        self._stats["rows_dropped_nan"] = rows_before - rows_after
        logger.info(
            "Inf→NaN replacement: %d column(s). Dropped %d NaN rows.",
            len(inf_cols),
            rows_before - rows_after,
        )
        return df

    def _drop_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """Drop exact duplicate rows (keep first occurrence)."""
        rows_before = len(df)
        df = df.drop_duplicates(keep="first")
        rows_after = len(df)
        self._stats["rows_dropped_duplicates"] = rows_before - rows_after
        logger.info("Dropped %d duplicate rows.", rows_before - rows_after)
        return df

    def _encode_labels(self, df: pd.DataFrame) -> pd.Series:
        """
        Apply label normalisation + integer encoding to the target column.

        Labels are normalised via ``normalize_raw_label`` (strips U+FFFD,
        collapses spaces) then mapped through YAML → AttackCategory → int index.
        Rows that remain UNKNOWN after normalisation are dropped with a warning.
        """
        if TARGET_COLUMN not in df.columns:
            raise ValueError(f"Target column '{TARGET_COLUMN}' not found in DataFrame.")

        raw_labels = df[TARGET_COLUMN]
        categories = raw_labels.apply(encode_label)

        from ml.preprocessing.data_dictionary import AttackCategory

        unknown_mask = categories == AttackCategory.UNKNOWN
        unknown_count = unknown_mask.sum()
        if unknown_count > 0:
            unknown_vals = raw_labels[unknown_mask].unique()
            logger.warning(
                "Dropping %d rows with UNKNOWN label (not in attack_mapping.yaml): %s",
                unknown_count,
                list(unknown_vals),
            )
            df = df[~unknown_mask]
            categories = categories[~unknown_mask]

        self._stats["unknown_labels_dropped"] = int(unknown_count)

        # Encode category string → integer index
        encoded = categories.apply(lambda cat: CATEGORY_TO_INDEX.get(cat.value, -1))
        self._stats["label_distribution"] = (
            df[TARGET_COLUMN]
            .apply(normalize_raw_label)
            .value_counts()
            .to_dict()
        )
        logger.info(
            "Label encoding complete. %d classes, %d rows.",
            encoded.nunique(),
            len(encoded),
        )
        return encoded

    def _split(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> tuple[
        pd.DataFrame,
        pd.DataFrame,
        pd.DataFrame,
        pd.Series,
        pd.Series,
        pd.Series,
    ]:
        """Stratified train / val / test split."""
        # First: split off test set
        X_trainval, X_test, y_trainval, y_test = train_test_split(
            X,
            y,
            test_size=self.test_size,
            stratify=y,
            random_state=self.random_state,
        )
        # Then: split train off from val
        val_fraction_of_trainval = self.val_size / (1.0 - self.test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_trainval,
            y_trainval,
            test_size=val_fraction_of_trainval,
            stratify=y_trainval,
            random_state=self.random_state,
        )
        logger.info(
            "Stratified split → train: %d  val: %d  test: %d",
            len(X_train),
            len(X_val),
            len(X_test),
        )
        return X_train, X_val, X_test, y_train, y_val, y_test
