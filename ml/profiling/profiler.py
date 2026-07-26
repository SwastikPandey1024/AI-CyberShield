"""
Dataset Profiler

Core profiling engine that computes comprehensive statistics and quality metrics
for cybersecurity datasets. Designed to work with CICIDS2017 and similar
network traffic datasets.

This module handles:
- Dataset-level summary statistics (rows, columns, memory usage)
- Per-column data quality metrics (missing values, duplicates, cardinality)
- Target column analysis (class distribution, balance ratios)
- Statistical summaries (mean, std, min, max, quantiles)
- Data type inference and categorization

Usage:
    from ml.profiling.profiler import DatasetProfiler

    profiler = DatasetProfiler(target_column="Label")
    profile = profiler.profile(df)
    # profile is a dict with all computed metrics
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Optional

import numpy as np
import pandas as pd


@dataclass
class ColumnProfile:
    """Profiling results for a single column."""

    column_name: str
    dtype: str
    count: int
    missing_count: int
    missing_ratio: float
    unique_count: int
    unique_ratio: float
    is_numeric: bool
    is_categorical: bool
    is_target: bool = False

    # Numeric statistics (only populated for numeric columns)
    mean: Optional[float] = None
    std: Optional[float] = None
    min: Optional[float] = None
    max: Optional[float] = None
    q25: Optional[float] = None
    q50: Optional[float] = None
    q75: Optional[float] = None
    skewness: Optional[float] = None
    kurtosis: Optional[float] = None
    infinity_count: int = 0
    zero_count: int = 0
    negative_count: int = 0

    # Categorical statistics (only populated for categorical/object columns)
    top_values: list[tuple[str, int]] = field(default_factory=list)
    cardinality: int = 0


@dataclass
class DatasetProfile:
    """Aggregate profiling results for the entire dataset."""

    file_name: str
    row_count: int
    column_count: int
    total_missing_cells: int
    total_missing_ratio: float
    total_duplicate_rows: int
    total_duplicate_ratio: float
    memory_usage_bytes: int
    memory_usage_mb: float
    estimated_rows: int = 0
    estimated_columns: int = 0

    # Column-level profiles
    columns: list[ColumnProfile] = field(default_factory=list)

    # Target analysis (if target column exists)
    target_column: Optional[str] = None
    class_distribution: dict[str, int] = field(default_factory=dict)
    class_ratios: dict[str, float] = field(default_factory=dict)
    class_balance_ratio: Optional[float] = None
    num_classes: int = 0

    # Data quality flags
    has_missing_values: bool = False
    has_duplicates: bool = False
    has_infinite_values: bool = False
    has_negative_values: bool = False
    has_constant_columns: bool = False
    has_high_cardinality: bool = False

    # Warnings
    warnings: list[str] = field(default_factory=list)


class DatasetProfiler:
    """
    Computes comprehensive profiling statistics for a pandas DataFrame.

    The profiler analyzes:
    - Dataset shape, memory usage, data types
    - Per-column missing values, uniqueness, statistics
    - Target column class distribution and balance
    - Data quality issues (infinite, negative, constant values)

    Usage:
        profiler = DatasetProfiler(target_column="Label")
        profile = profiler.profile(df, file_name="Monday-WorkingHours.csv")
        print(profile.row_count, profile.class_distribution)
    """

    def __init__(
        self,
        target_column: str = "Label",
        high_cardinality_threshold: int = 100,
    ) -> None:
        """
        Initialize the profiler.

        Args:
            target_column: Name of the target/label column for classification tasks.
                           Defaults to "Label" which is standard for CICIDS datasets.
            high_cardinality_threshold: Number of unique values above which a
                                        categorical column is flagged as high cardinality.
        """
        self._target_column = target_column
        self._high_cardinality_threshold = high_cardinality_threshold

    def profile(
        self,
        df: pd.DataFrame,
        file_name: str = "unknown.csv",
    ) -> DatasetProfile:
        """
        Run all profiling checks against the DataFrame.

        Args:
            df: The DataFrame to profile.
            file_name: Name of the source file for identification in reports.

        Returns:
            DatasetProfile containing all computed metrics and quality flags.
        """
        profile = DatasetProfile(
            file_name=file_name,
            row_count=len(df),
            column_count=len(df.columns),
            total_missing_cells=int(df.isna().sum().sum()),
            total_missing_ratio=float(df.isna().sum().sum() / df.size) if df.size > 0 else 0.0,
            total_duplicate_rows=int(df.duplicated().sum()),
            total_duplicate_ratio=float(df.duplicated().sum() / len(df)) if len(df) > 0 else 0.0,
            memory_usage_bytes=int(df.memory_usage(deep=True).sum()),
            memory_usage_mb=float(df.memory_usage(deep=True).sum() / (1024 * 1024)),
            estimated_rows=len(df),
            estimated_columns=len(df.columns),
        )

        # Per-column profiling
        for col in df.columns:
            col_profile = self._profile_column(df, col)
            profile.columns.append(col_profile)

        # Target column analysis
        if self._target_column in df.columns:
            self._analyze_target(df, profile)

        # Data quality flags
        self._set_quality_flags(profile)

        return profile

    def _profile_column(self, df: pd.DataFrame, column: str) -> ColumnProfile:
        """
        Profile a single column.

        Args:
            df: The DataFrame containing the column.
            column: Name of the column to profile.

        Returns:
            ColumnProfile with all computed statistics.
        """
        series = df[column]
        is_numeric = pd.api.types.is_numeric_dtype(series)
        is_target = column == self._target_column
        total = len(series)
        missing = int(series.isna().sum())
        unique = int(series.nunique())

        col_profile = ColumnProfile(
            column_name=column,
            dtype=str(series.dtype),
            count=total,
            missing_count=missing,
            missing_ratio=float(missing / total) if total > 0 else 0.0,
            unique_count=unique,
            unique_ratio=float(unique / total) if total > 0 else 0.0,
            is_numeric=is_numeric,
            is_categorical=not is_numeric or series.dtype == "object",
            is_target=is_target,
            cardinality=unique,
        )

        if is_numeric and not is_target:
            self._profile_numeric(series, col_profile)
        elif not is_numeric or is_target:
            self._profile_categorical(series, col_profile)

        return col_profile

    def _profile_numeric(self, series: pd.Series, col_profile: ColumnProfile) -> None:
        """
        Compute numeric statistics for a column.

        Args:
            series: The numeric series to analyze.
            col_profile: Mutable ColumnProfile to update.
        """
        clean = series.dropna()
        if len(clean) == 0:
            return

        col_profile.mean = float(clean.mean())
        col_profile.std = float(clean.std())
        col_profile.min = float(clean.min())
        col_profile.max = float(clean.max())
        col_profile.q25 = float(clean.quantile(0.25))
        col_profile.q50 = float(clean.quantile(0.50))
        col_profile.q75 = float(clean.quantile(0.75))
        col_profile.skewness = float(clean.skew())
        col_profile.kurtosis = float(clean.kurtosis())
        col_profile.infinity_count = int(series.isin([np.inf, -np.inf]).sum())
        col_profile.zero_count = int((clean == 0).sum())
        col_profile.negative_count = int((clean < 0).sum())

    def _profile_categorical(self, series: pd.Series, col_profile: ColumnProfile) -> None:
        """
        Compute categorical statistics for a column.

        Args:
            series: The categorical series to analyze.
            col_profile: Mutable ColumnProfile to update.
        """
        clean = series.dropna()
        if len(clean) == 0:
            return

        value_counts = clean.value_counts()
        top_k = min(10, len(value_counts))
        col_profile.top_values = list(
            value_counts.head(top_k).items()
        )
        col_profile.cardinality = int(clean.nunique())

    def _analyze_target(
        self,
        df: pd.DataFrame,
        profile: DatasetProfile,
    ) -> None:
        """
        Analyze the target column for class distribution and balance.

        Args:
            df: The DataFrame containing the target column.
            profile: Mutable DatasetProfile to update.
        """
        target = df[self._target_column].dropna()
        profile.target_column = self._target_column

        class_counts = target.value_counts()
        profile.class_distribution = class_counts.to_dict()
        profile.num_classes = len(class_counts)

        total = len(target)
        profile.class_ratios = {
            str(k): float(v / total) for k, v in class_counts.items()
        }

        # Compute class balance ratio (min / max)
        if len(class_counts) > 1:
            max_class = class_counts.max()
            min_class = class_counts.min()
            profile.class_balance_ratio = float(min_class / max_class) if max_class > 0 else 0.0
        else:
            profile.class_balance_ratio = 1.0

        # Warn about severe imbalance
        if profile.class_balance_ratio is not None and profile.class_balance_ratio < 0.1:
            profile.warnings.append(
                f"Severe class imbalance detected: ratio={profile.class_balance_ratio:.4f}. "
                "Consider resampling techniques."
            )

    def _set_quality_flags(self, profile: DatasetProfile) -> None:
        """
        Set data quality flags based on computed metrics.

        Args:
            profile: Mutable DatasetProfile to update.
        """
        profile.has_missing_values = profile.total_missing_cells > 0
        profile.has_duplicates = profile.total_duplicate_rows > 0

        for col in profile.columns:
            if col.infinity_count > 0:
                profile.has_infinite_values = True
            if col.negative_count > 0:
                profile.has_negative_values = True
            if col.unique_count == 1 and not col.is_target:
                profile.has_constant_columns = True
                profile.warnings.append(
                    f"Column '{col.column_name}' is constant (single value). "
                    "Consider dropping for modeling."
                )
            if col.cardinality > self._high_cardinality_threshold and col.is_categorical:
                profile.has_high_cardinality = True
                profile.warnings.append(
                    f"Column '{col.column_name}' has high cardinality "
                    f"({col.cardinality} unique values). Consider encoding or binning."
                )

        if profile.total_missing_ratio > 0.5:
            profile.warnings.append(
                f"Dataset has {profile.total_missing_ratio:.1%} missing values overall. "
                "Review column-level missing ratios."
            )


def profile_to_dict(profile: DatasetProfile) -> dict[str, Any]:
    """
    Convert a DatasetProfile to a JSON-serializable dictionary.

    Args:
        profile: The DatasetProfile to convert.

    Returns:
        Dict with all profile data suitable for JSON serialization.
    """
    return {
        "file_name": profile.file_name,
        "row_count": profile.row_count,
        "column_count": profile.column_count,
        "total_missing_cells": profile.total_missing_cells,
        "total_missing_ratio": round(profile.total_missing_ratio, 6),
        "total_duplicate_rows": profile.total_duplicate_rows,
        "total_duplicate_ratio": round(profile.total_duplicate_ratio, 6),
        "memory_usage_bytes": profile.memory_usage_bytes,
        "memory_usage_mb": round(profile.memory_usage_mb, 2),
        "target_column": profile.target_column,
        "num_classes": profile.num_classes,
        "class_distribution": profile.class_distribution,
        "class_ratios": {k: round(v, 6) for k, v in profile.class_ratios.items()},
        "class_balance_ratio": round(profile.class_balance_ratio, 6) if profile.class_balance_ratio else None,
        "has_missing_values": profile.has_missing_values,
        "has_duplicates": profile.has_duplicates,
        "has_infinite_values": profile.has_infinite_values,
        "has_negative_values": profile.has_negative_values,
        "has_constant_columns": profile.has_constant_columns,
        "has_high_cardinality": profile.has_high_cardinality,
        "warnings": profile.warnings,
        "columns": [
            {
                "column_name": c.column_name,
                "dtype": c.dtype,
                "count": c.count,
                "missing_count": c.missing_count,
                "missing_ratio": round(c.missing_ratio, 6),
                "unique_count": c.unique_count,
                "unique_ratio": round(c.unique_ratio, 6),
                "is_numeric": c.is_numeric,
                "is_categorical": c.is_categorical,
                "is_target": c.is_target,
                "mean": round(c.mean, 6) if c.mean is not None else None,
                "std": round(c.std, 6) if c.std is not None else None,
                "min": c.min,
                "max": c.max,
                "q25": round(c.q25, 6) if c.q25 is not None else None,
                "q50": round(c.q50, 6) if c.q50 is not None else None,
                "q75": round(c.q75, 6) if c.q75 is not None else None,
                "skewness": round(c.skewness, 6) if c.skewness is not None else None,
                "kurtosis": round(c.kurtosis, 6) if c.kurtosis is not None else None,
                "infinity_count": c.infinity_count,
                "zero_count": c.zero_count,
                "negative_count": c.negative_count,
                "cardinality": c.cardinality,
                "top_values": [
                    {"value": str(v), "count": int(cnt)}
                    for v, cnt in c.top_values
                ],
            }
            for c in profile.columns
        ],
    }
