"""
Inference wrapper:
- Loads NN artifacts (if present), else falls back to Deliverable1 hybrid.
- Provides score_url(url, alpha, fetch_html) with star mapping and timeouts.
- Designed to be imported by API and Gradio space.
"""

import json, asyncio, functools, joblib, numpy as np, pandas as pd
from pathlib import Path
from typing import Dict
from Deliverable1 import evaluate_credibility, extract_features, FeatureConfig, hybrid_score

ARTDIR = Path(__file__).parent / "artifacts"
HAS_NN = (ARTDIR / "mlp_pipeline.joblib").exists()

if HAS_NN:
    PIPE = joblib.load(ARTDIR / "mlp_pipeline.joblib")
    TS   = joblib.load(ARTDIR / "temp_scaler.joblib")
    FEATS = json.loads((ARTDIR / "features.json").read_text())

def _nn_prob(url: str, fetch_html=False) -> float:
    X = extract_features(url, FeatureConfig(fetch_html=fetch_html))
    # align feature columns
    X = X.reindex(columns=FEATS, fill_value=0)
    try:
        lg = PIPE.decision_function(X)
    except Exception:
        p = PIPE.predict_proba(X)[:,1].clip(1e-6, 1-1e-6)
        lg = np.log(p/(1-p))
    return float(TS.predict_proba(lg)[0,1])

def stars_from_score(s: float) -> int:
    return 5 if s>=0.80 else 4 if s>=0.65 else 3 if s>=0.50 else 2 if s>=0.35 else 1

async def score_url(url: str, alpha: float = 0.5, fetch_html: bool = False,
                    timeout_s: float = 3.0) -> Dict[str, object]:
    """
    Async entrypoint with timeout + fallback:
    - If NN artifacts exist, blend NN prob with rule score (alpha applies to NN).
    - If anything times out/fails, fall back to Deliverable1.hybrid_score (robust).
    """
    async def _work():
        rule = evaluate_credibility(url)["score"]
        if HAS_NN:
            ml = await asyncio.to_thread(_nn_prob, url, fetch_html)
            final = float(np.clip(alpha*ml + (1-alpha)*rule, 0.0, 1.0))
            explanation = f"NN+Rules blend (α={alpha:.2f}). Rule={rule:.2f}, NN={ml:.2f}."
        else:
            res = await asyncio.to_thread(hybrid_score, url, alpha, fetch_html)
            final, explanation = res["score"], res["explanation"]
        return {
            "score": round(final,3),
            "stars": stars_from_score(final),
            "explanation": explanation
        }
    try:
        return await asyncio.wait_for(_work(), timeout=timeout_s)
    except Exception as e:
        # Hard fallback: rule-only
        rb = evaluate_credibility(url)
        return {"score": rb["score"], "stars": stars_from_score(rb["score"]),
                "explanation": f"Fallback to rules due to: {e}. {rb['explanation']}"}
