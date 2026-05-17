"""Fraud scoring API: XGBoost model + metadata (feature order, threshold, positive class)."""

from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from fastapi import FastAPI, HTTPException, status, Body
from pydantic import BaseModel, ConfigDict, create_model

import csv
import io

MAX_ROWS_ALLOWED = 5

_BASE = Path(__file__).resolve().parent # get the parent folder of main.py

with open(_BASE / "metadata.json", encoding="utf-8") as f:
    meta: dict = json.load(f)

feature_names: list[str] = list(meta["feature_names"])
threshold: float = float(meta["threshold"])
positive_label: int = int(meta["positive_label"])

model = joblib.load(_BASE / "model.joblib")

_cl = getattr(model, "classes_", None)
_classes = [int(c) for c in (_cl if _cl is not None else [0, 1])]
if positive_label not in _classes:
    raise ValueError(
        f"positive_label={positive_label} is not in model.classes_={_classes}; "
        "fix metadata or retrain so they agree."
    )
# Column of predict_proba for P(fraud == positive_label)
_proba_col: int = int(_classes.index(positive_label))

PredictRequest = create_model(
    "PredictRequest",
    __config__=ConfigDict(extra="ignore"),
    **{name: (float, ...) for name in feature_names},
)

class PredictResponse(BaseModel):
    probability_fraud: float
    predicted_fraud: int

class HealthResponse(BaseModel):
    ok: bool

app = FastAPI(title="Fraud prediction API")

@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(ok=True)

@app.post("/v1/predict", response_model=PredictResponse)
def predict(body: PredictRequest) -> PredictResponse:  # type: ignore[valid-type]
    row = [getattr(body, name) for name in feature_names]
    X = np.array([row], dtype=np.float32)
    proba = float(model.predict_proba(X)[0, _proba_col])
    label = int(proba >= threshold)
    return PredictResponse(probability_fraud=proba, predicted_fraud=label)

@app.post("/v1/dict-from-string")
def build_dict_from_string(
    csv_data: str = Body(..., media_type="text/plain")
):
    csv_file = io.StringIO(csv_data)
    reader_as_dict = csv.DictReader(csv_file)

    dict_response = []
    row_count = 0

    for row in reader_as_dict:
        row_count += 1

        # row limit
        if row_count > MAX_ROWS_ALLOWED:
            raise HTTPException(
                status_code=status.HTTP_413_CONTENT_TOO_LARGE,
                details=f"Payload too large. Maximu allowed rows is {MAX_ROWS_ALLOWED}."
            )
        
        # append row to the dict_response
        print('===================')
        print(row)
        dict_response.append(row)

    # if the payload is empty
    if not dict_response:
        raise HTTPException(status_code=400, detail="Cannot get rows from payload.")

    # convert string in values to float
    for d in dict_response:
        for key, value in d.items():
            try:
                d[key] = float(value)
            except (ValueError, TypeError):
                print(f"Cound not convert '{value}' to a float.")
    
    return { "data": dict_response}