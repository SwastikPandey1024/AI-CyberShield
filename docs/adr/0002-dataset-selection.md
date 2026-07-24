# ADR 0002: Dataset Selection

**Status:** Accepted
**Date:** 2026
**Deciders:** Engineering Team

---

## Context

The ML model requires a labeled dataset of network traffic flows containing both benign and malicious activity. The dataset must be:
- Publicly available and freely distributable
- Large enough for training a robust ML model
- Representative of real-world network attacks
- Well-documented with ground truth labels
- Suitable for multi-class classification (multiple attack types)

## Decision

**Primary Dataset:** CICIDS2017 (Canadian Institute for Cybersecurity Intrusion Detection System 2017)

### Dataset Characteristics
- **Size:** ~2.8M records, 80+ features
- **Attack Types:** DDoS, Brute Force, Botnet, Port Scan, Web Attack, Infiltration, Benign
- **Format:** PCAP + CSV (extracted flow features)
- **Collection:** 5 days of real network traffic simulation
- **License:** Publicly available for research

## Alternatives Considered

| Dataset | Year | Records | Attack Types | Reason for Rejection (as primary) |
|---------|------|---------|-------------|-----------------------------------|
| **KDD Cup 99** | 1999 | ~4.9M | 4 | Outdated; not representative of modern traffic |
| **NSL-KDD** | 2009 | ~148K | 4 | Small; reduced version of KDD 99 |
| **UNSW-NB15** | 2015 | ~2.5M | 9 | Good alternative; will be used in future |
| **CSE-CIC-IDS2018** | 2018 | ~16M | 7 | Very large; harder to iterate with; future use |
| **TON-IoT** | 2020 | ~461K | 9 | Smaller; IoT-focused; future use |

## Consequences

### Positive
- CICIDS2017 is the most widely used benchmark in ML-based IDS research
- 80+ features provide rich signal for the model
- Multi-class labels enable fine-grained threat detection
- Extensive prior work makes baseline comparison possible

### Negative
- ~2.8M records can be memory-intensive; sampling needed for quick iteration
- Severe class imbalance (Benign dominates at ~80%)
- Some attack classes have very few samples (e.g., Infiltration, Heartbleed)
- Dataset is from 2017; newer attack patterns may be missing

### Mitigations
- Use stratified sampling during development; full dataset for final training
- Apply SMOTE + class weighting for imbalance handling
- Supplement with UNSW-NB15 and CSE-CIC-IDS2018 in future versions
