"""
Profiling Visualizations

Generates statistical plots and visualizations for dataset profiling reports.
All plots are saved as PNG files for inclusion in documentation and review.

This module handles:
- Class distribution bar charts
- Missing value heatmaps
- Numeric feature distribution histograms
- Correlation heatmaps
- Data quality summary dashboards

Usage:
    from ml.profiling.visualizations import ProfilingVisualizer

    visualizer = ProfilingVisualizer(output_dir="reports/data/profiling/figures")
    visualizer.plot_class_distribution(profile, dataset_name="Monday-WorkingHours")
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for headless environments

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

from ml.profiling.profiler import DatasetProfile


# Set default style
sns.set_style("whitegrid")
plt.rcParams["figure.figsize"] = (12, 6)
plt.rcParams["figure.dpi"] = 100


class ProfilingVisualizer:
    """
    Generates and saves profiling visualizations to disk.

    All plots are saved as PNG files in the configured output directory.
    Each dataset gets its own subdirectory for organized storage.

    Usage:
        visualizer = ProfilingVisualizer(
            output_dir="reports/data/profiling/figures"
        )
        visualizer.plot_class_distribution(profile, dataset_name="Monday-WorkingHours")
        visualizer.plot_missing_heatmap(df, dataset_name="Monday-WorkingHours")
    """

    def __init__(
        self,
        output_dir: str | Path = "reports/data/profiling/figures",
    ) -> None:
        """
        Initialize the visualizer.

        Args:
            output_dir: Root directory for saving plot images.
                        Per-dataset subdirectories will be created under this.
        """
        self._output_dir = Path(output_dir)
        self._output_dir.mkdir(parents=True, exist_ok=True)

    def plot_class_distribution(
        self,
        profile: DatasetProfile,
        dataset_name: str,
    ) -> Optional[Path]:
        """
        Plot the target class distribution as a bar chart.

        Args:
            profile: DatasetProfile with target analysis data.
            dataset_name: Name of the dataset for file naming.

        Returns:
            Path to the saved PNG file, or None if no target column exists.
        """
        if not profile.class_distribution:
            return None

        fig, ax = plt.subplots()
        classes = list(profile.class_distribution.keys())
        counts = list(profile.class_distribution.values())
        colors = plt.cm.Set2(np.linspace(0, 1, len(classes)))

        bars = ax.bar(classes, counts, color=colors, edgecolor="black", linewidth=0.5)
        ax.set_xlabel("Attack Category")
        ax.set_ylabel("Count")
        ax.set_title(f"Class Distribution: {profile.file_name}")
        ax.tick_params(axis="x", rotation=45)

        # Add count labels on bars
        for bar, count in zip(bars, counts):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{count:,}",
                ha="center",
                va="bottom",
                fontsize=8,
            )

        plt.tight_layout()
        path = self._get_path(dataset_name, "class_distribution.png")
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def plot_missing_heatmap(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        max_columns: int = 50,
    ) -> Path:
        """
        Plot a heatmap of missing values across columns.

        For datasets with many columns, only the first max_columns are shown.

        Args:
            df: DataFrame to visualize missing values for.
            dataset_name: Name of the dataset for file naming.
            max_columns: Maximum number of columns to display.

        Returns:
            Path to the saved PNG file.
        """
        # Select columns with missing values, limit to max_columns
        missing_cols = df.columns[df.isna().any()].tolist()
        if not missing_cols:
            # Create an empty plot indicating no missing values
            fig, ax = plt.subplots(figsize=(8, 2))
            ax.text(
                0.5, 0.5, "No missing values found",
                ha="center", va="center", fontsize=14,
            )
            ax.set_title(f"Missing Values: {dataset_name}")
            ax.axis("off")
            path = self._get_path(dataset_name, "missing_values.png")
            fig.savefig(path, bbox_inches="tight")
            plt.close(fig)
            return path

        cols_to_plot = missing_cols[:max_columns]
        missing_matrix = df[cols_to_plot].isna()

        fig, ax = plt.subplots(figsize=(12, max(4, len(cols_to_plot) * 0.3)))
        sns.heatmap(
            missing_matrix.T,
            cbar=False,
            cmap="RdYlGn_r",
            ax=ax,
            yticklabels=cols_to_plot,
        )
        ax.set_title(f"Missing Value Heatmap: {dataset_name}")
        ax.set_xlabel("Row Index")
        ax.set_ylabel("Columns")

        plt.tight_layout()
        path = self._get_path(dataset_name, "missing_values.png")
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def plot_feature_distributions(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        max_features: int = 20,
    ) -> list[Path]:
        """
        Plot histograms for numeric features.

        Args:
            df: DataFrame with numeric features.
            dataset_name: Name of the dataset for file naming.
            max_features: Maximum number of features to plot.

        Returns:
            List of paths to saved PNG files.
        """
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        # Exclude target column if it's numeric
        numeric_cols = [c for c in numeric_cols if c != "Label"]
        cols_to_plot = numeric_cols[:max_features]

        paths: list[Path] = []
        for col in cols_to_plot:
            fig, ax = plt.subplots(figsize=(10, 4))
            clean = df[col].dropna()
            clean = clean[~np.isinf(clean)]

            if len(clean) == 0:
                ax.text(0.5, 0.5, "No valid data", ha="center", va="center")
            else:
                ax.hist(clean, bins=50, edgecolor="black", alpha=0.7, color="steelblue")
                ax.axvline(
                    clean.mean(), color="red", linestyle="--",
                    label=f"Mean: {clean.mean():.2f}",
                )
                ax.axvline(
                    clean.median(), color="green", linestyle="--",
                    label=f"Median: {clean.median():.2f}",
                )

            ax.set_title(f"Distribution: {col}")
            ax.set_xlabel(col)
            ax.set_ylabel("Frequency")
            ax.legend()

            plt.tight_layout()
            safe_col = col.replace("/", "_").replace(" ", "_")
            path = self._get_path(dataset_name, f"dist_{safe_col}.png")
            fig.savefig(path, bbox_inches="tight")
            plt.close(fig)
            paths.append(path)

        return paths

    def plot_correlation_heatmap(
        self,
        df: pd.DataFrame,
        dataset_name: str,
        max_features: int = 30,
    ) -> Optional[Path]:
        """
        Plot a correlation heatmap for numeric features.

        Args:
            df: DataFrame with numeric features.
            dataset_name: Name of the dataset for file naming.
            max_features: Maximum number of features to include.

        Returns:
            Path to the saved PNG file, or None if insufficient numeric columns.
        """
        numeric_df = df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return None

        cols_to_plot = numeric_df.columns[:max_features]
        corr_matrix = numeric_df[cols_to_plot].corr()

        fig, ax = plt.subplots(figsize=(14, 12))
        mask = np.triu(np.ones_like(corr_matrix, dtype=bool), k=1)
        sns.heatmap(
            corr_matrix,
            mask=mask,
            cmap="RdBu_r",
            center=0,
            vmin=-1,
            vmax=1,
            square=True,
            linewidths=0.5,
            cbar_kws={"shrink": 0.8},
            ax=ax,
        )
        ax.set_title(f"Feature Correlation Heatmap: {dataset_name}")
        ax.tick_params(axis="x", rotation=90)
        ax.tick_params(axis="y", rotation=0)

        plt.tight_layout()
        path = self._get_path(dataset_name, "correlation_heatmap.png")
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def plot_data_quality_dashboard(
        self,
        profile: DatasetProfile,
        dataset_name: str,
    ) -> Path:
        """
        Plot a data quality summary dashboard.

        Shows missing ratio, duplicate ratio, class balance, and memory usage
        in a single figure.

        Args:
            profile: DatasetProfile with quality metrics.
            dataset_name: Name of the dataset for file naming.

        Returns:
            Path to the saved PNG file.
        """
        fig, axes = plt.subplots(2, 2, figsize=(12, 8))

        # Top-left: Missing & Duplicate ratios
        ax = axes[0, 0]
        metrics = ["Missing", "Duplicates"]
        values = [profile.total_missing_ratio * 100, profile.total_duplicate_ratio * 100]
        colors = ["coral" if v > 5 else "lightgreen" for v in values]
        bars = ax.bar(metrics, values, color=colors, edgecolor="black")
        ax.set_ylabel("Percentage (%)")
        ax.set_title("Data Quality Overview")
        for bar, val in zip(bars, values):
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height(),
                f"{val:.2f}%",
                ha="center", va="bottom",
            )

        # Top-right: Class balance
        ax = axes[0, 1]
        if profile.class_distribution:
            classes = list(profile.class_distribution.keys())
            counts = list(profile.class_distribution.values())
            colors = plt.cm.Set3(np.linspace(0, 1, len(classes)))
            ax.pie(
                counts, labels=classes, autopct="%1.1f%%",
                colors=colors, startangle=90,
            )
            ax.set_title(f"Class Distribution ({profile.num_classes} classes)")
        else:
            ax.text(0.5, 0.5, "No target column", ha="center", va="center")
            ax.set_title("Class Distribution")

        # Bottom-left: Memory usage
        ax = axes[1, 0]
        mem_metrics = ["Memory (MB)"]
        mem_values = [profile.memory_usage_mb]
        ax.bar(mem_metrics, mem_values, color="steelblue", edgecolor="black")
        ax.set_ylabel("MB")
        ax.set_title(f"Memory Usage: {profile.memory_usage_mb:.2f} MB")
        ax.text(0, profile.memory_usage_mb, f"{profile.memory_usage_mb:.2f} MB",
                ha="center", va="bottom")

        # Bottom-right: Dataset shape
        ax = axes[1, 1]
        ax.axis("off")
        info_text = (
            f"Dataset: {profile.file_name}\n"
            f"Rows: {profile.row_count:,}\n"
            f"Columns: {profile.column_count}\n"
            f"Missing Cells: {profile.total_missing_cells:,}\n"
            f"Duplicate Rows: {profile.total_duplicate_rows:,}\n"
            f"Warnings: {len(profile.warnings)}"
        )
        ax.text(0.1, 0.5, info_text, va="center", fontsize=11,
                bbox=dict(boxstyle="round", facecolor="lightgray", alpha=0.5))
        ax.set_title("Dataset Info")

        plt.suptitle(f"Data Quality Dashboard: {dataset_name}", fontsize=14, y=1.02)
        plt.tight_layout()
        path = self._get_path(dataset_name, "data_quality_dashboard.png")
        fig.savefig(path, bbox_inches="tight")
        plt.close(fig)
        return path

    def _get_path(self, dataset_name: str, filename: str) -> Path:
        """
        Get the full path for a plot file, creating subdirectories as needed.

        Args:
            dataset_name: Name of the dataset.
            filename: Name of the plot file (e.g. "class_distribution.png").

        Returns:
            Full Path to the plot file.
        """
        safe_name = dataset_name.replace(".csv", "").replace(".pcap_ISCX", "")
        safe_name = safe_name.replace(" ", "_").replace("/", "_")
        subdir = self._output_dir / safe_name
        subdir.mkdir(parents=True, exist_ok=True)
        return subdir / filename
