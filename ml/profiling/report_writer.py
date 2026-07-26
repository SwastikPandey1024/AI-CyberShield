"""
Report Writer

Generates structured profiling reports in multiple formats (JSON, Markdown, CSV)
from DatasetProfile objects. Each report type serves a different audience:

- JSON: Machine-readable for downstream pipeline consumption
- Markdown: Human-readable for documentation and review
- CSV: Tabular format for spreadsheet analysis and comparison across files

Usage:
    from ml.profiling.profiler import DatasetProfiler
    from ml.profiling.report_writer import ReportWriter

    profiler = DatasetProfiler()
    profile = profiler.profile(df, file_name="Monday-WorkingHours.csv")

    writer = ReportWriter(output_dir="reports/data/profiling/Monday-WorkingHours")
    writer.write_all(profile, dataset_name="Monday-WorkingHours")
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

import pandas as pd

from ml.profiling.profiler import DatasetProfile, profile_to_dict


class ReportWriter:
    """
    Writes profiling reports to disk in multiple formats.

    Creates per-file subdirectories under the output root, each containing:
    - summary.json: Machine-readable profile data
    - summary.md: Human-readable markdown report
    - statistics.csv: Per-column numeric statistics
    - missing_values.csv: Per-column missing value counts
    - duplicates.csv: Duplicate row summary
    - cardinality.csv: Per-column cardinality stats
    - class_distribution.csv: Target class distribution (if target exists)

    Usage:
        writer = ReportWriter(output_dir="reports/data/profiling")
        writer.write_all(profile, dataset_name="Monday-WorkingHours")
    """

    def __init__(self, output_dir: str | Path = "reports/data/profiling") -> None:
        """
        Initialize the report writer.

        Args:
            output_dir: Root directory for profiling reports.
                        Per-file subdirectories will be created under this.
        """
        self._output_dir = Path(output_dir)

    def write_all(
        self,
        profile: DatasetProfile,
        dataset_name: str,
    ) -> Path:
        """
        Write all report formats for a single dataset profile.

        Args:
            profile: The DatasetProfile to write reports for.
            dataset_name: Name of the dataset (used for subdirectory naming).

        Returns:
            Path to the created subdirectory.
        """
        safe_name = self._sanitize_name(dataset_name)
        report_dir = self._output_dir / safe_name
        report_dir.mkdir(parents=True, exist_ok=True)

        self._write_summary_json(profile, report_dir)
        self._write_summary_md(profile, report_dir)
        self._write_statistics_csv(profile, report_dir)
        self._write_missing_values_csv(profile, report_dir)
        self._write_duplicates_csv(profile, report_dir)
        self._write_cardinality_csv(profile, report_dir)
        self._write_class_distribution_csv(profile, report_dir)

        return report_dir

    def _sanitize_name(self, name: str) -> str:
        """
        Sanitize a dataset name for use as a directory name.

        Args:
            name: Raw dataset name (e.g. "Monday-WorkingHours.pcap_ISCX.csv").

        Returns:
            Sanitized name safe for filesystem use.
        """
        # Remove .csv extension and sanitize
        base = name.replace(".csv", "").replace(".pcap_ISCX", "")
        return base.replace(" ", "_").replace("/", "_").replace("\\", "_")

    def _write_summary_json(
        self,
        profile: DatasetProfile,
        report_dir: Path,
    ) -> None:
        """
        Write the full profile as a JSON file.

        Args:
            profile: DatasetProfile to serialize.
            report_dir: Directory to write the file in.
        """
        data = profile_to_dict(profile)
        data["generated_at"] = datetime.utcnow().isoformat()
        data["profiling_tool"] = "AI CyberShield Profiler v0.1.0"

        path = report_dir / "summary.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)

    def _write_summary_md(
        self,
        profile: DatasetProfile,
        report_dir: Path,
    ) -> None:
        """
        Write a human-readable markdown summary report.

        Args:
            profile: DatasetProfile to format.
            report_dir: Directory to write the file in.
        """
        lines: list[str] = []
        lines.append(f"# Dataset Profile: {profile.file_name}")
        lines.append("")
        lines.append(f"*Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}*")
        lines.append("")
        lines.append("## Dataset Summary")
        lines.append("")
        lines.append(f"| Metric | Value |")
        lines.append(f"|--------|-------|")
        lines.append(f"| Rows | {profile.row_count:,} |")
        lines.append(f"| Columns | {profile.column_count} |")
        lines.append(f"| Memory Usage | {profile.memory_usage_mb:.2f} MB |")
        lines.append(f"| Missing Cells | {profile.total_missing_cells:,} ({profile.total_missing_ratio:.2%}) |")
        lines.append(f"| Duplicate Rows | {profile.total_duplicate_rows:,} ({profile.total_duplicate_ratio:.2%}) |")
        lines.append("")

        if profile.target_column:
            lines.append("## Target Analysis")
            lines.append("")
            lines.append(f"| Metric | Value |")
            lines.append(f"|--------|-------|")
            lines.append(f"| Target Column | {profile.target_column} |")
            lines.append(f"| Number of Classes | {profile.num_classes} |")
            lines.append(f"| Class Balance Ratio | {profile.class_balance_ratio:.4f} |")
            lines.append("")
            lines.append("### Class Distribution")
            lines.append("")
            lines.append("| Class | Count | Ratio |")
            lines.append("|-------|-------|-------|")
            for cls, count in sorted(profile.class_distribution.items(), key=lambda x: -x[1]):
                ratio = profile.class_ratios.get(cls, 0.0)
                lines.append(f"| {cls} | {count:,} | {ratio:.4%} |")
            lines.append("")

        lines.append("## Data Quality Flags")
        lines.append("")
        lines.append(f"| Flag | Status |")
        lines.append(f"|------|--------|")
        lines.append(f"| Missing Values | {'⚠️' if profile.has_missing_values else '✅'} |")
        lines.append(f"| Duplicates | {'⚠️' if profile.has_duplicates else '✅'} |")
        lines.append(f"| Infinite Values | {'⚠️' if profile.has_infinite_values else '✅'} |")
        lines.append(f"| Negative Values | {'⚠️' if profile.has_negative_values else '✅'} |")
        lines.append(f"| Constant Columns | {'⚠️' if profile.has_constant_columns else '✅'} |")
        lines.append(f"| High Cardinality | {'⚠️' if profile.has_high_cardinality else '✅'} |")
        lines.append("")

        if profile.warnings:
            lines.append("## Warnings")
            lines.append("")
            for warning in profile.warnings:
                lines.append(f"- ⚠️ {warning}")
            lines.append("")

        path = report_dir / "summary.md"
        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

    def _write_statistics_csv(
        self,
        profile: DatasetProfile,
        report_dir: Path,
    ) -> None:
        """
        Write per-column numeric statistics as a CSV file.

        Args:
            profile: DatasetProfile with column data.
            report_dir: Directory to write the file in.
        """
        rows: list[dict[str, Any]] = []
        for col in profile.columns:
            if col.is_numeric:
                rows.append({
                    "column": col.column_name,
                    "dtype": col.dtype,
                    "count": col.count,
                    "missing": col.missing_count,
                    "missing_ratio": col.missing_ratio,
                    "mean": col.mean,
                    "std": col.std,
                    "min": col.min,
                    "q25": col.q25,
                    "q50": col.q50,
                    "q75": col.q75,
                    "max": col.max,
                    "skewness": col.skewness,
                    "kurtosis": col.kurtosis,
                    "infinity_count": col.infinity_count,
                    "zero_count": col.zero_count,
                    "negative_count": col.negative_count,
                })

        if rows:
            df = pd.DataFrame(rows)
            path = report_dir / "statistics.csv"
            df.to_csv(path, index=False)

    def _write_missing_values_csv(
        self,
        profile: DatasetProfile,
        report_dir: Path,
    ) -> None:
        """
        Write per-column missing value counts as a CSV file.

        Args:
            profile: DatasetProfile with column data.
            report_dir: Directory to write the file in.
        """
        rows: list[dict[str, Any]] = []
        for col in profile.columns:
            rows.append({
                "column": col.column_name,
                "dtype": col.dtype,
                "total": col.count,
                "missing_count": col.missing_count,
                "missing_ratio": col.missing_ratio,
                "non_missing": col.count - col.missing_count,
            })

        if rows:
            df = pd.DataFrame(rows)
            path = report_dir / "missing_values.csv"
            df.to_csv(path, index=False)

    def _write_duplicates_csv(
        self,
        profile: DatasetProfile,
        report_dir: Path,
    ) -> None:
        """
        Write duplicate row summary as a CSV file.

        Args:
            profile: DatasetProfile with duplicate info.
            report_dir: Directory to write the file in.
        """
        rows = [
            {"metric": "total_rows", "value": profile.row_count},
            {"metric": "duplicate_rows", "value": profile.total_duplicate_rows},
            {"metric": "duplicate_ratio", "value": f"{profile.total_duplicate_ratio:.4%}"},
            {"metric": "unique_rows", "value": profile.row_count - profile.total_duplicate_rows},
        ]

        df = pd.DataFrame(rows)
        path = report_dir / "duplicates.csv"
        df.to_csv(path, index=False)

    def _write_cardinality_csv(
        self,
        profile: DatasetProfile,
        report_dir: Path,
    ) -> None:
        """
        Write per-column cardinality stats as a CSV file.

        Args:
            profile: DatasetProfile with column data.
            report_dir: Directory to write the file in.
        """
        rows: list[dict[str, Any]] = []
        for col in profile.columns:
            rows.append({
                "column": col.column_name,
                "dtype": col.dtype,
                "unique_count": col.unique_count,
                "unique_ratio": col.unique_ratio,
                "cardinality": col.cardinality,
                "is_categorical": col.is_categorical,
                "is_numeric": col.is_numeric,
            })

        if rows:
            df = pd.DataFrame(rows)
            path = report_dir / "cardinality.csv"
            df.to_csv(path, index=False)

    def _write_class_distribution_csv(
        self,
        profile: DatasetProfile,
        report_dir: Path,
    ) -> None:
        """
        Write target class distribution as a CSV file.

        Args:
            profile: DatasetProfile with target analysis.
            report_dir: Directory to write the file in.
        """
        if not profile.class_distribution:
            return

        rows: list[dict[str, Any]] = []
        for cls, count in sorted(profile.class_distribution.items(), key=lambda x: -x[1]):
            ratio = profile.class_ratios.get(cls, 0.0)
            rows.append({
                "class": cls,
                "count": count,
                "ratio": ratio,
            })

        if rows:
            df = pd.DataFrame(rows)
            path = report_dir / "class_distribution.csv"
            df.to_csv(path, index=False)
