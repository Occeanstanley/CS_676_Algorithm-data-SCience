"""
Train a small neural network (MLP) on the same features used by Deliverable1.
- Novelty: nonlinear fusion of rule score + URL/content features.
- Calibrated probabilities via simple Temperature Scaling.
- Exports artifacts to ./artifacts/
"""

import json, math, joblib, numpy as np, pandas as pd
from pathlib import Path
from dataclasses import dataclass
from typing import List, Tuple
from sklearn.neural_network import MLPClassifier
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.metrics import log_loss

# Reuse your feature extractor & seed labels
from Deliverable1 import extract_features, FeatureConfig, SEED_TRAIN

ARTDIR = Path(__file__).parent / "artifacts"
ARTDIR.mkdir(exist_ok=True)

def _build_Xy(rows: List[Tuple[str,int]], fetch_html=False):
    cfg = FeatureConfig(fetch_html=fetch_html)
    Xr, y = [], []
    for url, label in rows:
        Xr.append(extract_features(url, cfg))
        y.append(int(label))
    X = pd.concat(Xr, ignore_index=True)
    return X, np.array(y, dtype=int)

@dataclass
class TemperatureScaler:
    T: float = 1.0
    def fit(self, logits, y):
        # Simple 1D line-search to minimize NLL; robust for small data
        best_T, best_ll = 1.0, 1e9
        for T in np.linspace(0.5, 3.0, 51):
            p = 1 / (1 + np.exp(-logits / T))
            ll = log_loss(y, np.c_[1-p, p])
            if ll < best_ll:
                best_ll, best_T = ll, T
        self.T = float(best_T)
        return self
    def predict_proba(self, logits):
        p = 1 / (1 + np.exp(-logits / self.T))
        return np.c_[1-p, p]

def main(fetch_html: bool = False, random_state: int = 42):
    X, y = _build_Xy(SEED_TRAIN, fetch_html=fetch_html)
    feat_names = list(X.columns)

    # Pipeline: impute -> scale -> MLP (2 hidden layers)
    pipe = Pipeline([
        ("imputer", SimpleImputer(strategy="constant", fill_value=0)),
        ("scaler", StandardScaler(with_mean=False)),
        ("mlp", MLPClassifier(hidden_layer_sizes=(16, 8),
                              activation="relu", solver="adam",
                              max_iter=800, random_state=random_state))
    ])

    # Hold-out split (tiny data → 20% test)
    Xtr, Xte, ytr, yte = train_test_split(
        X, y, test_size=0.2, random_state=random_state, stratify=y if y.min()<y.max() else None
    )
    pipe.fit(Xtr, ytr)

    # Get logits (use decision_function; fallback to logit from proba)
    def logits(model, Xframe):
        try:
            return model.decision_function(Xframe)
        except Exception:
            p = model.predict_proba(Xframe)[:,1].clip(1e-6, 1-1e-6)
            return np.log(p/(1-p))

    # Temperature scale on the test partition
    lg = logits(pipe, Xte)
    scaler = TemperatureScaler().fit(lg, yte)

    # Save artifacts
    joblib.dump(pipe, ARTDIR / "mlp_pipeline.joblib")
    joblib.dump(scaler, ARTDIR / "temp_scaler.joblib")
    (ARTDIR / "features.json").write_text(json.dumps(feat_names, indent=2))
    print("Saved artifacts to", ARTDIR)

if __name__ == "__main__":
    main(fetch_html=False)
