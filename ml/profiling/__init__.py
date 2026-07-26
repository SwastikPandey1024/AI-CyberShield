"""
AI CyberShield — Data Profiling Package

Provides comprehensive dataset profiling capabilities for cybersecurity datasets.
Computes dataset summary statistics, data quality metrics, target analysis,
and generates structured reports (JSON, Markdown, CSVs) and visualizations.

Modules:
    profiler: Core profiling engine
    report_writer: Structured report generation (JSON, MD, CSV)
    visualizations: Statistical plot generation (PNG)
    run_profiling: CLI entry point for batch profiling
"""

from ml.profiling.profiler import DatasetProfiler
from ml.profiling.report_writer import ReportWriter
from ml.profiling.visualizations import ProfilingVisualizer

__all__ = [
    "DatasetProfiler",
    "ReportWriter",
    "ProfilingVisualizer",
]
