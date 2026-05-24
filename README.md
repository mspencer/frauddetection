# Credit Card Fraud Detection API

A lightweight FastAPI service designed to take raw CSV input rows, parse them into a structured key-value array, and pass them to a pre-trained scikit-learn model for fraud prediction.

---

## 🛠 Model Training & Artifacts

### Where Artifacts Go
The production API requires two files inside the `api/` directory:
1. `api/model.joblib` — The serialized trained model object (e.g., RandomForest, LogisticRegression).
2. `api/metadata.json` — Accompanying training metadata, thresholds, or feature engineering configurations.

### How to Train and Update
When training a new model version:
1. Run your training notebook/script locally or in your pipeline.
2. Export the final model artifact using `joblib`:
   ```python
   import joblib
   joblib.dump(trained_model, "api/model.joblib")