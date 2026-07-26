# ADR-0003: CICIDS2017 Dataset Selection

## Status
Accepted

## Date
2026-07-26

## Context
The MVP requires a labeled network traffic dataset for training a multi-class threat detection model. The dataset must be publicly available, realistic, contain diverse attack types, and be large enough to train a generalizable model.

## Decision
Select **CICIDS2017** as the primary dataset for the MVP.

Key factors:
- **Modern**: Captured in 2017, still widely used as a benchmark.
- **Realistic**: Includes benign traffic and up-to-date attack scenarios (DDoS, Brute Force, Botnet, Port Scan, Web Attack, Infiltration).
- **Large**: ~2.8M labeled flows across 80+ features — sufficient for training production-quality models.
- **Multi-class**: 15 attack categories plus benign, enabling fine-grained threat classification.
- **Well-documented**: Extensive literature and pre-processing scripts available.

## Alternatives Considered
- **CSE-CIC-IDS2018**: Larger but more redundant features; deferred to future versions.
- **UNSW-NB15**: Smaller and older; useful as a secondary evaluation set.
- **TON-IoT**: More recent but less community validation; considered for v2.

## Consequences
- CICIDS2017's class imbalance (Benign dominates ~80%) requires stratified sampling and class weighting.
- The 80+ feature set will need dimensionality reduction or feature selection.
- Dataset is ~5GB+ when fully extracted; a 10-20% stratified subset will be used for rapid iteration.
