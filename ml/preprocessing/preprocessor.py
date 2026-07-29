"""
Preprocessing Pipeline — Phase 2.6b
=====================================

Evidence-driven preprocessing for the CICIDS2017 dataset.
Every decision in this module is directly justified by an empirical finding
in ``reports/data/eda/findings.md`` (Phase 2.5, 2026-07-29).

Pipeline Steps & Justifications (cited from findings.md):
---------------------------------------------------------
1. Constant Columns (findings.md Step 1):
   - 8 columns constant in all files, 2 constant in 7/8 files.
   - NOT dropped during preprocessing. Flagged in ``configs/datasets/cicids2017/schema.yaml``
     under ``drop_candidates`` for Milestone 3 modeling verification.

2. Missing Values (findings.md Step 2):
   - 1,358 rows (0.048% of dataset) isolated strictly to ``Flow Bytes/s``.
   - Row-level drop is applied instead of imputation because 0.048% is a negligible
     sample size, avoiding artificial variance distortion.

3. Duplicate Rows (findings.md Step 3):
   - 256,479 duplicate rows (9.06% aggregate, up to 25.26% in PortScan).
   - Removed PER FILE (before merging and before splitting) to preserve file-level semantics.
   - Extreme BENIGN concentration (e.g. 99.5% of duplicates in DDoS file) flagged for
     re-examination if class balance work is undertaken in Milestone 3.

4. Infinity Values (findings.md Step 4):
   - Inf in ``Flow Bytes/s`` and ``Flow Packets/s`` has 100% co-occurrence with ``Flow Duration == 0``.
   - Replaced with 0 (not NaN, not drop). Division by zero in instantaneous captures means
     rate = 0 is the semantically correct value.

5. Negative Values in Init_Win_bytes_* (findings.md Step 4):
   - ``Init_Win_bytes_backward`` (30-62%) and ``Init_Win_bytes_forward`` (14-50%) contain -1.
   - Kept as-is. -1 is an intentional CICFlowMeter sentinel ("window size not observed"),
     not corrupted data. Model must learn this sentinel value.

6. Exact Duplicate Columns (findings.md Step 5):
   - 7 columns confirmed identical to primary columns (r = 1.0000, CICFlowMeter definition).
   - Dynamically verified identical before dropping:
     * Subflow Fwd Packets == Total Fwd Packets
     * Subflow Bwd Packets == Total Backward Packets
     * Subflow Fwd Bytes == Total Length of Fwd Packets
     * Subflow Bwd Bytes == Total Length of Bwd Packets
     * Avg Fwd Segment Size == Fwd Packet Length Mean
     * Avg Bwd Segment Size == Bwd Packet Length Mean
     * Fwd Header Length.1 == Fwd Header Length
   - 82 remaining correlated pairs (|r| > 0.90) retained intact for Milestone 3 feature selection.

7. Class Imbalance (findings.md Step 6):
   - 206,645:1 imbalance ratio. Resampling explicitly deferred to Milestone 3 modeling.
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
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

TARGET_COLUMN = "Label"

# 7 exact duplicate columns to verify and drop (findings.md Step 5)
EXACT_DUPLICATE_PAIRS: list[tuple[str, str]] = [
    ("Subflow Fwd Packets", "Total Fwd Packets"),
    ("Subflow Bwd Packets", "Total Backward Packets"),
    ("Subflow Fwd Bytes", "Total Length of Fwd Packets"),
    ("Subflow Bwd Bytes", "Total Length of Bwd Packets"),
    ("Avg Fwd Segment Size", "Fwd Packet Length Mean"),
    ("Avg Bwd Segment Size", "Bwd Packet Length Mean"),
    ("Fwd Header Length.1", "Fwd Header Length"),
]


@dataclass
class PreprocessingResult:
    """Output container for preprocessed splits, scaler, and audit metadata."""

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


class CICIDSPreprocessor:
    """
    Reusable, config-driven preprocessing pipeline for CICIDS2017.
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
        self._stats: dict[str, Any] = {
            "per_file_before_after": {},
            "verified_exact_duplicates": [],
            "dropped_columns": [],
            "inf_replaced_count": 0,
            "missing_rows_dropped": 0,
            "total_per_file_duplicates_dropped": 0,
        }

    def fit_transform(
        self,
        csv_dir: Path,
        *,
        glob_pattern: str = "*.csv",
    ) -> PreprocessingResult:
        """
        Run the full evidence-driven preprocessing pipeline.
        """
        # Step A: Load files and remove per-file duplicates (findings.md Step 3)
        df = self._load_and_deduplicate_per_file(csv_dir, glob_pattern)

        # Step B: Verify and drop 7 exact duplicate columns (findings.md Step 5)
        df = self._verify_and_drop_exact_duplicates(df)

        # Step C: Replace Inf with 0 for zero-duration flows (findings.md Step 4)
        df = self._replace_infinities_with_zero(df)

        # Step D: Drop rows with missing values (findings.md Step 2)
        df = self._drop_missing_value_rows(df)

        # Step E: Encode labels (findings.md Step 0)
        y = self._encode_labels(df)
        X = df.drop(columns=[TARGET_COLUMN])

        # Step F: Stratified train / val / test split (findings.md Step 6)
        X_train, X_val, X_test, y_train, y_val, y_test = self._split(X, y)

        # Step G: Fit RobustScaler on train set, transform all splits
        # RobustScaler handles Init_Win_bytes_* sentinel -1 values without mean/std distortion
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

        label_names = {v: k for k, v in CATEGORY_TO_INDEX.items()}

        self._stats["split_sizes"] = {
            "train": len(X_train_scaled),
            "val": len(X_val_scaled),
            "test": len(X_test_scaled),
        }
        self._stats["n_features"] = len(X_train_scaled.columns)

        logger.info(
            "Pipeline complete: train=%d, val=%d, test=%d, features=%d",
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

    def _load_and_deduplicate_per_file(self, csv_dir: Path, glob_pattern: str) -> pd.DataFrame:
        """
        Load each CSV file, normalize column names, remove duplicate rows PER FILE,
        and log before/after counts.
        Cites findings.md Step 3.
        """
        csv_files = sorted(csv_dir.glob(glob_pattern))
        if not csv_files:
            raise FileNotFoundError(f"No CSV files found in {csv_dir}")

        normalizer = ColumnNormalizer()
        frames: list[pd.DataFrame] = []
        total_raw_rows = 0

        for path in csv_files:
            df = pd.read_csv(path, low_memory=False)
            df.columns = normalizer.normalize_columns(list(df.columns))
            rows_before = len(df)
            total_raw_rows += rows_before

            # Per-file deduplication (findings.md Step 3)
            df = df.drop_duplicates(keep="first")
            rows_after = len(df)
            dups_dropped = rows_before - rows_after

            self._stats["per_file_before_after"][path.name] = {
                "raw_rows": rows_before,
                "dedup_rows": rows_after,
                "duplicates_dropped": dups_dropped,
                "duplicate_pct": round((dups_dropped / rows_before) * 100, 2),
            }
            self._stats["total_per_file_duplicates_dropped"] += dups_dropped

            logger.info(
                "Loaded %s: %d → %d rows (%d duplicates dropped, %.2f%%)",
                path.name,
                rows_before,
                rows_after,
                dups_dropped,
                (dups_dropped / rows_before) * 100,
            )
            frames.append(df)

        combined = pd.concat(frames, ignore_index=True)
        self._stats["raw_rows_total"] = total_raw_rows
        self._stats["combined_rows_after_file_dedup"] = len(combined)
        return combined

    def _verify_and_drop_exact_duplicates(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Verify that 7 candidate exact-duplicate column pairs are 100% identical
        before dropping the secondary column.
        Cites findings.md Step 5.
        """
        cols_to_drop = []
        for dup_col, primary_col in EXACT_DUPLICATE_PAIRS:
            if dup_col in df.columns and primary_col in df.columns:
                # Runtime empirical verification of exact equality
                is_identical = np.array_equal(
                    df[dup_col].to_numpy(na_value=np.nan),
                    df[primary_col].to_numpy(na_value=np.nan),
                    equal_nan=True,
                )
                if is_identical:
                    cols_to_drop.append(dup_col)
                    self._stats["verified_exact_duplicates"].append(
                        {"column": dup_col, "identical_to": primary_col, "verified": True}
                    )
                    logger.info("VERIFIED: '%s' is 100%% identical to '%s' -> marked for drop.", dup_col, primary_col)
                else:
                    logger.warning("MISMATCH: '%s' is NOT 100%% identical to '%s' -> NOT dropping.", dup_col, primary_col)

        df = df.drop(columns=cols_to_drop)
        self._stats["dropped_columns"] = cols_to_drop
        return df

    def _replace_infinities_with_zero(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Replace Infinity values in Flow Bytes/s and Flow Packets/s with 0.
        Cites findings.md Step 4 (100% co-occurrence with Flow Duration == 0).
        """
        inf_count = 0
        for col in ["Flow Bytes/s", "Flow Packets/s"]:
            if col in df.columns:
                inf_mask = np.isinf(df[col])
                inf_in_col = int(inf_mask.sum())
                if inf_in_col > 0:
                    df.loc[inf_mask, col] = 0.0
                    inf_count += inf_in_col
                    logger.info("Replaced %d infinity values with 0 in '%s'", inf_in_col, col)

        self._stats["inf_replaced_count"] = inf_count
        return df

    def _drop_missing_value_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop rows with missing values (1,358 rows, 0.048%, strictly Flow Bytes/s).
        Cites findings.md Step 2.
        """
        rows_before = len(df)
        df = df.dropna()
        rows_after = len(df)
        dropped = rows_before - rows_after
        self._stats["missing_rows_dropped"] = dropped
        logger.info("Dropped %d rows containing missing values (%.4f%% of dataset)", dropped, (dropped / rows_before) * 100)
        return df

    def _encode_labels(self, df: pd.DataFrame) -> pd.Series:
        """
        Encode raw label strings to category integer indices.
        Cites findings.md Step 0.
        """
        if TARGET_COLUMN not in df.columns:
            raise ValueError(f"Target column '{TARGET_COLUMN}' not found.")

        raw_labels = df[TARGET_COLUMN]
        categories = raw_labels.apply(encode_label)

        from ml.preprocessing.data_dictionary import AttackCategory

        unknown_mask = categories == AttackCategory.UNKNOWN
        if unknown_mask.sum() > 0:
            logger.warning("Dropping %d UNKNOWN label rows", int(unknown_mask.sum()))
            df = df[~unknown_mask]
            categories = categories[~unknown_mask]

        encoded = categories.apply(lambda cat: CATEGORY_TO_INDEX.get(cat.value, -1))
        return encoded

    def _split(
        self,
        X: pd.DataFrame,
        y: pd.Series,
    ) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.Series, pd.Series, pd.Series]:
        """Stratified train / val / test split."""
        X_trainval, X_test, y_trainval, y_test = train_test_split(
            X,
            y,
            test_size=self.test_size,
            stratify=y,
            random_state=self.random_state,
        )
        val_fraction = self.val_size / (1.0 - self.test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_trainval,
            y_trainval,
            test_size=val_fraction,
            stratify=y_trainval,
            random_state=self.random_state,
        )
        return X_train, X_val, X_test, y_train, y_val, y_test
