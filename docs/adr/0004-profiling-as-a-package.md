# ADR-0004: Profiling as a Package

## Status
Accepted

## Date
2026-07-26

## Context
The data profiling engine needs to analyze the CICIDS2017 dataset for missing values, distributions, correlations, and class balance. This functionality could be implemented as a single module, a collection of scripts, or a dedicated Python package.

## Decision
Implement profiling as a standalone Python package under `ml/preprocessing/profiling/` with a clear public API.

- The package exposes a `ProfileReport` class that accepts a DataFrame and configuration, and produces structured reports (JSON + visualizations).
- Internal modules are separated by concern: `univariate.py`, `bivariate.py`, `missing.py`, `report.py`.
- Reports are saved to `reports/data/profiling/` with timestamps.

## Alternatives Considered
- **Single monolithic module**: Rejected — would become unmanageable as profiling capabilities grow (univariate stats, bivariate correlations, missing value analysis, class balance).
- **Jupyter notebook**: Rejected — not reusable in automated pipelines or CI.
- **Third-party library (ydata-profiling)**: Considered but rejected for MVP for the following reasons:
  1. **Performance**: ydata-profiling generates comprehensive HTML reports with embedded visualizations, which is computationally expensive for large datasets. On a 2.5M-row CICIDS2017 file, ydata-profiling can take 5-10+ minutes and consume >4GB RAM, while our custom profiler completes in under 30 seconds with <500MB RAM by computing only the statistics we need.
  2. **Output control**: ydata-profiling produces a single HTML file that is difficult to parse programmatically. Our profiler outputs structured JSON, Markdown, and CSV files that can be consumed by downstream pipeline stages.
  3. **Domain-specific metrics**: ydata-profiling lacks cybersecurity-specific metrics like class imbalance ratios, attack category distributions, and network traffic feature analysis that our domain requires.
  4. **CI/CD compatibility**: ydata-profiling's HTML reports are not suitable for automated diffing or comparison across dataset versions. Our structured outputs enable programmatic regression detection.

  Future versions may wrap ydata-profiling for ad-hoc exploratory analysis while keeping our custom profiler for automated pipeline runs.

## Consequences
- Profiling logic is testable in isolation.
- The package can be imported in both notebooks and automated scripts.
- Adding new profiling metrics (e.g., time-series analysis for flow duration) is straightforward.
- TODO: needs Tech Lead input on whether to eventually wrap ydata-profiling for advanced reports while keeping our custom metrics.
