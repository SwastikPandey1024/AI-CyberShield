# ADR 0004: XGBoost as ML Algorithm

**Status:** Accepted
**Date:** 2024
**Deciders:** Engineering Team

---

## Context

The ML model must classify network traffic flows as benign or malicious (multi-class). Requirements:
- High accuracy on tabular data (80+ features, ~2.8M records)
- Fast inference time (< 500ms per prediction)
- Built-in handling of missing values
- Feature importance for explainability
- Support for class imbalance handling
- Reproducible training with deterministic results

## Decision

**Algorithm:** XGBoost (eXtreme Gradient Boosting)

### Key Features Used
- **Gradient boosted decision trees** for high accuracy
- **Multi-class softmax** objective for attack type classification
- **Scale_pos_weight** for class imbalance
- **Early stopping** to prevent overfitting
- **Feature importance** (gain, cover, frequency) for explainability
- **GPU support** for faster training (optional)

## Alternatives Considered

| Alternative | Pros | Cons |
|-------------|------|------|
| **Random Forest** | Simple, parallelizable | Lower accuracy; larger model size |
| **LightGBM** | Faster training, lower memory | Can overfit on small datasets; leaf-wise growth |
| **CatBoost** | Handles categorical features natively | Slower; less community adoption |
| **Logistic Regression** | Fast, interpretable | Poor performance on complex patterns |
| **Neural Networks** | Flexible, powerful | Overkill for tabular data; harder to train |

## Consequences

### Positive
- XGBoost consistently wins Kaggle competitions on tabular data
- Built-in handling of missing values and categorical features
- Feature importance scores provide built-in explainability
- Well-documented API with scikit-learn compatibility
- Efficient CPU and GPU training

### Negative
- Hyperparameter tuning is critical (many parameters)
- Can overfit without proper regularization (early stopping, max_depth)
- Model size can be large with many trees (100s of MB)
- Not inherently interpretable like linear models (requires SHAP for deep explanations)

### Mitigations
- Use cross-validation with early stopping
- Set conservative max_depth (6–10) and learning_rate (0.01–0.1)
- Use subsample and colsample_bytree for regularization
- Save SHAP explanations alongside predictions for interpretability
