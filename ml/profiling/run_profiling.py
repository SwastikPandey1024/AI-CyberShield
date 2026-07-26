"""
Data Profiling Runner

CLI entry point for running the profiling engine against all CICIDS2017 dataset files.

This module orchestrates:
1. Loading each CSV file using DatasetLoader
2. Profiling each DataFrame using DatasetProfiler
3. Writing structured reports using ReportWriter
4. Generating visualizations using ProfilingVisualizer
5. Aggregating a cross-file summary report

Usage:
    python -m ml.profiling.run_profiling
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any

from ml.preprocessing.dataset_loader import DatasetLoader
from ml.profiling.profiler import DatasetProfiler
from ml.profiling.report_writer import ReportWriter
from ml.profiling.visualizations import ProfilingVisualizer


# Paths
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATASET_DIR = PROJECT_ROOT / "datasets" / "raw" / "CICIDS2017"
REPORT_DIR = PROJECT_ROOT / "reports" / "data" / "profiling"
FIGURE_DIR = REPORT_DIR / "figures"

# Expected CICIDS2017 files
CICIDS2017_FILES: list[str] = [
    "Monday-WorkingHours.pcap_ISCX.csv",
    "Tuesday-WorkingHours.pcap_ISCX.csv",
    "Wednesday-workingHours.pcap_ISCX.csv",
    "Thursday-WorkingHours-Morning-WebAttacks.pcap_ISCX.csv",
    "Thursday-WorkingHours-Afternoon-Infilteration.pcap_ISCX.csv",
    "Friday-WorkingHours-Morning.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-DDos.pcap_ISCX.csv",
    "Friday-WorkingHours-Afternoon-PortScan.pcap_ISCX.csv",
]


def profile_single_file(
    file_path: Path,
    loader: DatasetLoader,
    profiler: DatasetProfiler,
    writer: ReportWriter,
    visualizer: ProfilingVisualizer,
) -> dict[str, Any]:
    """
    Profile a single CICIDS2017 CSV file.

    Args:
        file_path: Path to the CSV file.
        loader: DatasetLoader instance.
        profiler: DatasetProfiler instance.
        writer: ReportWriter instance.
        visualizer: ProfilingVisualizer instance.

    Returns:
        Dict with profiling results including timing and file info.
    """
    file_name = file_path.name
    print(f"  Loading {file_name}...")

    load_start = time.time()
    df = loader.load(str(file_path))
    load_time = time.time() - load_start
    print(f"    Loaded {len(df):,} rows x {len(df.columns)} columns in {load_time:.2f}s")

    profile_start = time.time()
    profile = profiler.profile(df, file_name=file_name)
    profile_time = time.time() - profile_start
    print(f"    Profiled in {profile_time:.2f}s")

    report_start = time.time()
    report_dir = writer.write_all(profile, dataset_name=file_name)
    report_time = time.time() - report_start
    print(f"    Reports written to {report_dir}")

    viz_start = time.time()
    try:
        visualizer.plot_class_distribution(profile, dataset_name=file_name)
        visualizer.plot_missing_heatmap(df, dataset_name=file_name)
        visualizer.plot_data_quality_dashboard(profile, dataset_name=file_name)
        visualizer.plot_correlation_heatmap(df, dataset_name=file_name)
    except Exception as e:
        print(f"    Warning: Visualization error: {e}")
    viz_time = time.time() - viz_start
    print(f"    Visualizations generated in {viz_time:.2f}s")

    return {
        "file_name": file_name,
        "rows": profile.row_count,
        "columns": profile.column_count,
        "load_time_s": round(load_time, 2),
        "profile_time_s": round(profile_time, 2),
        "report_time_s": round(report_time, 2),
        "viz_time_s": round(viz_time, 2),
        "total_time_s": round(load_time + profile_time + report_time + viz_time, 2),
        "memory_mb": profile.memory_usage_mb,
        "missing_cells": profile.total_missing_cells,
        "missing_ratio": profile.total_missing_ratio,
        "duplicate_rows": profile.total_duplicate_rows,
        "duplicate_ratio": profile.total_duplicate_ratio,
        "num_classes": profile.num_classes if profile.target_column else 0,
        "class_balance_ratio": profile.class_balance_ratio if profile.target_column else None,
        "warnings_count": len(profile.warnings),
    }


def run_pipeline() -> None:
    """Run the full profiling pipeline across all CICIDS2017 files."""
    print("=" * 70)
    print("AI CyberShield — Data Profiling Engine")
    print("=" * 70)
    print(f"Dataset directory: {DATASET_DIR}")
    print(f"Report directory:  {REPORT_DIR}")
    print()

    # Validate dataset directory exists
    if not DATASET_DIR.exists():
        print(f"ERROR: Dataset directory not found: {DATASET_DIR}")
        print("Please ensure CICIDS2017 CSV files are in datasets/raw/CICIDS2017/")
        sys.exit(1)

    # Initialize components
    loader = DatasetLoader()
    profiler = DatasetProfiler(target_column="Label")
    writer = ReportWriter(output_dir=str(REPORT_DIR))
    visualizer = ProfilingVisualizer(output_dir=str(FIGURE_DIR))

    # Discover available files
    available_files = [f for f in CICIDS2017_FILES if (DATASET_DIR / f).exists()]
    missing_files = [f for f in CICIDS2017_FILES if not (DATASET_DIR / f).exists()]

    print(f"Found {len(available_files)}/{len(CICIDS2017_FILES)} CICIDS2017 files")
    if missing_files:
        print(f"Missing {len(missing_files)} files: {', '.join(missing_files)}")
    print()

    if not available_files:
        print("No CICIDS2017 files found. Nothing to profile.")
        sys.exit(0)

    # Profile each file
    all_results: list[dict[str, Any]] = []
    pipeline_start = time.time()

    for i, file_name in enumerate(available_files, 1):
        file_path = DATASET_DIR / file_name
        print(f"[{i}/{len(available_files)}] Profiling: {file_name}")
        print(f"  File size: {file_path.stat().st_size / (1024*1024):.1f} MB")

        try:
            result = profile_single_file(
                file_path, loader, profiler, writer, visualizer,
            )
            all_results.append(result)
            status = "✓" if result["warnings_count"] == 0 else "⚠"
            print(f"  {status} Done ({result['total_time_s']}s total)")
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            all_results.append({
                "file_name": file_name,
                "error": str(e),
                "total_time_s": 0,
            })

        print()

    total_time = time.time() - pipeline_start

    # Print summary table
    print("=" * 70)
    print("PROFILING SUMMARY")
    print("=" * 70)
    print(f"{'File':<45} {'Rows':>10} {'Cols':>5} {'Missing':>8} {'Dup %':>8} {'Classes':>7} {'Time':>6}")
    print("-" * 70)
    for r in all_results:
        if "error" in r and r.get("error"):
            print(f"{r['file_name']:<45} {'ERROR':>10} {'':>5} {'':>8} {'':>8} {'':>7} {'':>6}")
        else:
            missing_str = f"{r['missing_cells']:,}" if r["missing_cells"] > 0 else "0"
            dup_str = f"{r['duplicate_ratio']:.1%}" if r["duplicate_ratio"] > 0 else "0%"
            classes_str = str(r["num_classes"]) if r["num_classes"] > 0 else "N/A"
            time_str = f"{r['total_time_s']:.1f}s"
            print(
                f"{r['file_name']:<45} {r['rows']:>10,} {r['columns']:>5} "
                f"{missing_str:>8} {dup_str:>8} {classes_str:>7} {time_str:>6}"
            )
    print("-" * 70)
    print(f"Total files profiled: {len(available_files)}")
    print(f"Total pipeline time:  {total_time:.1f}s")
    print(f"Report output:        {REPORT_DIR}")
    print("=" * 70)


if __name__ == "__main__":
    run_pipeline()
