
"""
Hybrid Credibility Scorer (Rules + Light ML with Adaptive CV Calibration)

Exposes:
- evaluate_credibility(url: str) -> {"score": float, "explanation": str}
- hybrid_score(url: str, alpha: float = 0.5, fetch_html: bool = False)
    -> {"score": float, "explanation": str}

CLI:
  python hybrid_deliverable.py --url "https://who.int/news/item/..." --alpha 0.5
  python hybrid_deliverable.py --smoke
  python hybrid_deliverable.py --url "..." --fetch-html --json-out out.json
"""

from __future__ import annotations

from urllib.parse import urlparse
from dataclasses import dataclass
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import argparse, json, math, re, sys

import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.calibration import CalibratedClassifierCV
from sklearn.model_selection import train_test_split
from sklearn.impute import SimpleImputer

# Optional deps (only used if --fetch-html)
try:
    import requests
except Exception:
    requests = None
try:
    from bs4 import BeautifulSoup
except Exception:
    BeautifulSoup = None

# =========================
# 1) Rule-based baseline
# =========================

REPUTABLE_DOMAINS = {
    "nih.gov","ncbi.nlm.nih.gov","cdc.gov","who.int","nature.com","science.org",
    "sciencedirect.com","nejm.org","thelancet.com","bmj.com","jamanetwork.com",
    "plos.org","ox.ac.uk","harvard.edu","stanford.edu","mit.edu","webmd.com"
}

def _clip01(x: float) -> float:
    return 1.0 if x > 1.0 else (0.0 if x < 0.0 else x)

def evaluate_credibility(url: str) -> Dict[str, object]:
    """Offline, transparent rule-based scorer."""
    if not isinstance(url, str) or not url.strip():
        return {"score": 0.0, "explanation": "Invalid input: URL must be a non-empty string."}
    try:
        parsed = urlparse(url.strip())
        explanation_parts: List[str] = []
        score = 0.30  # base

        host = (parsed.netloc or "").lower()
        path_lc = (parsed.path or "").lower()

        # 1) HTTPS
        if parsed.scheme == "https":
            score += 0.05; explanation_parts.append("Uses HTTPS (+0.05).")
        elif parsed.scheme in ("http", ""):
            explanation_parts.append("Missing HTTPS (0.00).")

        # 2) Institutional TLD
        tld = host.split(".")[-1] if host else ""
        if tld in {"gov","edu","ac"}:
            score += 0.25; explanation_parts.append(f"TLD '.{tld}' (institutional) (+0.25).")

        # 3) Recognized reputable domains
        if any(host == d or host.endswith("."+d) for d in REPUTABLE_DOMAINS):
            score += 0.25; explanation_parts.append(f"Recognized reputable domain '{host}' (+0.25).")

        # 4) Informal/blogging signals
        informal_hits = 0
        if "blog" in host or "/blog" in path_lc:
            informal_hits += 1; explanation_parts.append("Contains 'blog' in domain/path (-0.10).")
        for plat in ("medium.com","wordpress","substack"):
            if plat in host:
                informal_hits += 1; explanation_parts.append("Hosted on blogging platform (-0.10).")
        if informal_hits:
            score -= 0.10 * informal_hits

        # 5) DOI-like pattern
        if re.search(r"/10\.\d{4,9}/[-._;()/:A-Z0-9]+", path_lc or "", re.I):
            score += 0.20; explanation_parts.append("DOI-like identifier found (+0.20).")

        # 6) Tracking params
        q = (parsed.query or "").lower()
        if any(k in q for k in ("utm_","fbclid","gclid")):
            score -= 0.05; explanation_parts.append("Tracking params in query (-0.05).")

        # 7) Very short host
        if len(host) < 5:
            score -= 0.05; explanation_parts.append("Very short/unclear host (-0.05).")

        score = round(_clip01(score), 2)
        if not explanation_parts:
            explanation_parts.append("Applied neutral baseline heuristics.")
        return {"score": score, "explanation": " ".join(explanation_parts)}
    except Exception as e:
        return {"score": 0.0, "explanation": f"Error processing URL: {e}"}

# =========================
# 2) Feature extraction
# =========================

@dataclass
class FeatureConfig:
    fetch_html: bool = False
    timeout: int = 6

_DATE_META_KEYS = [
    ("meta", {"name": "date"}),
    ("meta", {"property": "article:published_time"}),
    ("meta", {"name": "pubdate"}),
    ("time",  {}),
]

def _safe_get(url: str, timeout: int) -> Optional[str]:
    if not requests or not BeautifulSoup:
        return None
    try:
        r = requests.get(url, timeout=timeout, headers={"User-Agent":"Mozilla/5.0"})
        if r.status_code == 200 and r.content:
            return r.text
    except Exception:
        pass
    return None

def _parse_date_from_html(soup: "BeautifulSoup") -> Optional[datetime]:
    for tag, attrs in _DATE_META_KEYS:
        for el in soup.find_all(tag, attrs=attrs):
            cand = el.get("content") or el.get_text(strip=True)
            if not cand:
                continue
            try:
                return datetime.fromisoformat(cand.replace("Z","").split("+")[0])
            except Exception:
                m = re.search(r"(20\d{2}|19\d{2})[-/\.](\d{1,2})[-/\.](\d{1,2})", cand)
                if m:
                    y, M, d = map(int, m.groups())
                    return datetime(y, M, d)
    return None

def _basic_readability(text: str):
    sents = re.split(r"[\.!\?]+", text or ""); sents = [s for s in sents if s.strip()]
    words = re.findall(r"\b[a-zA-Z]{2,}\b", text or "")
    n_sents = max(1, len(sents)); n_words = max(1, len(words))
    avg_wps = n_words / n_sents
    avg_cpw = (sum(len(w) for w in words) / len(words)) if words else 0.0
    return avg_wps, avg_cpw, (len(words) if words else 0)

def extract_features(url: str, cfg: FeatureConfig = FeatureConfig()) -> pd.DataFrame:
    rb = evaluate_credibility(url); rule_score = rb["score"]
    parsed = urlparse(url); host = (parsed.netloc or "").lower()
    path_lc = (parsed.path or "").lower()
    https_flag = 1 if parsed.scheme == "https" else 0
    tld = host.split(".")[-1] if host else ""
    inst_tld = 1 if tld in {"gov","edu","ac"} else 0
    rep_domain = 1 if any(host == d or host.endswith("."+d) for d in REPUTABLE_DOMAINS) else 0
    doi_in_path = 1 if re.search(r"/10\.\d{4,9}/[-._;()/:A-Z0-9]+", path_lc or "", re.I) else 0
    blog_flag = 1 if ("blog" in host or "/blog" in path_lc or any(p in host for p in ["medium.com","wordpress","substack"])) else 0
    tracking_flag = 1 if any(k in (parsed.query or "").lower() for k in ["utm_","gclid","fbclid"]) else 0
    short_host = 1 if len(host) < 5 else 0

    text = ""; days_since = math.nan
    if cfg.fetch_html and requests and BeautifulSoup:
        html = _safe_get(url, cfg.timeout)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            text = " ".join(p.get_text(" ", strip=True) for p in soup.find_all("p"))
            pub_dt = _parse_date_from_html(soup)
            if pub_dt:
                days_since = float((datetime.utcnow() - pub_dt).days)

    refs_brackets = len(re.findall(r"\[\d+\]", text)) if text else 0
    doi_mentions  = len(re.findall(r"\bdoi\b", text, flags=re.I)) if text else 0
    ref_keywords  = len(re.findall(r"\b(references?|citations?|journal|volume|issue|pmid)\b", text, flags=re.I)) if text else 0
    avg_wps, avg_cpw, n_words = _basic_readability(text) if text else (0.0, 0.0, 0)

    feats = {
        "rule_score": rule_score,
        "https": https_flag,
        "inst_tld": inst_tld,
        "reputable": rep_domain,
        "doi_in_path": doi_in_path,
        "blog_flag": blog_flag,
        "tracking_flag": tracking_flag,
        "short_host": short_host,
        "refs_brackets": refs_brackets,
        "doi_mentions": doi_mentions,
        "ref_keywords": ref_keywords,
        "avg_words_per_sent": float(avg_wps),
        "avg_chars_per_word": float(avg_cpw),
        "n_words": int(n_words),
        "days_since": float(days_since) if not math.isnan(days_since) else np.nan,
        "has_content": 1 if text else 0,
    }
    return pd.DataFrame([feats])

# =========================
# 3) Train + Adaptive CV
# =========================

SEED_TRAIN = [
    ("https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/", 1),
    ("https://who.int/news/item/2020-health-advisory",          1),
    ("https://www.webmd.com/back-pain/guide/spinal-stenosis",   1),
    ("https://doi.org/10.1038/s41586-020-2649-2",               1),
    ("https://medium.com/@someone/health-tips-123",             0),
    ("http://example.com/blog/opinion",                         0),
]

@dataclass
class HybridModel:
    imputer: SimpleImputer
    calibrator: Optional[CalibratedClassifierCV]   # may be None if too few samples
    features: List[str]
    explainer_lr: LogisticRegression               # used for explanations & fallback proba

def _make_imputer():
    # Prefer keeping empty features (newer sklearn), fallback gracefully
    try:
        return SimpleImputer(strategy="constant", fill_value=0, keep_empty_features=True)
    except TypeError:
        return SimpleImputer(strategy="constant", fill_value=0)

def _pick_cv(y, desired=3):
    """Pick a safe number of CV folds given class counts; return 0 to skip calibration."""
    _, counts = np.unique(y, return_counts=True)
    min_count = int(counts.min())
    if min_count < 2:
        return 0
    return max(2, min(desired, min_count))

def train_hybrid(train_data: List[Tuple[str, int]],
                 fetch_html: bool = False,
                 random_state: int = 42,
                 cv_folds: int = 3) -> HybridModel:
    """Train CV-calibrated classifier; fit a separate LR for explanations."""
    X_rows: List[pd.DataFrame] = []; y: List[int] = []
    cfg = FeatureConfig(fetch_html=fetch_html)
    for url, label in train_data:
        X_rows.append(extract_features(url, cfg)); y.append(int(label))
    X = pd.concat(X_rows, ignore_index=True); y = np.array(y, dtype=int)

    imp = _make_imputer()
    X_imp = pd.DataFrame(imp.fit_transform(X), columns=X.columns)

    # Split off a tiny test set (optional); train/calibrate on train portion
    X_tr, X_te, y_tr, y_te = train_test_split(
        X_imp, y, test_size=0.2, random_state=random_state, stratify=y
    )

    # Base LR for probabilities & explanations
    explainer_lr = LogisticRegression(max_iter=500)
    explainer_lr.fit(X_tr, y_tr)

    # Choose CV folds based on class counts; calibrate only if feasible
    n_splits = _pick_cv(y_tr, desired=cv_folds)
    if n_splits >= 2:
        calibrator = CalibratedClassifierCV(estimator=LogisticRegression(max_iter=500),
                                            cv=n_splits, method="sigmoid")
        calibrator.fit(X_tr, y_tr)
    else:
        calibrator = None  # too few samples per class; skip calibration

    return HybridModel(imputer=imp, calibrator=calibrator,
                       features=list(X.columns), explainer_lr=explainer_lr)

# =========================
# 4) Hybrid scoring
# =========================

def hybrid_score(url: str, alpha: float = 0.5,
                 trained: Optional[HybridModel] = None,
                 fetch_html: bool = False) -> Dict[str, object]:
    if trained is None:
        trained = train_hybrid(SEED_TRAIN, fetch_html=fetch_html)

    rb = evaluate_credibility(url); rule = float(rb["score"])
    feats = extract_features(url, FeatureConfig(fetch_html=fetch_html))
    feats_imp = pd.DataFrame(trained.imputer.transform(feats), columns=trained.features)

    proba_model = trained.calibrator if trained.calibrator is not None else trained.explainer_lr
    ml_prob = float(proba_model.predict_proba(feats_imp)[:, 1][0])

    final = float(np.clip(alpha * ml_prob + (1 - alpha) * rule, 0.0, 1.0))

    # Explanation via explainer LR’s coefficients (stable, human-readable)
    coef = getattr(trained.explainer_lr, "coef_", None)
    top_txt = "n/a"
    if coef is not None:
        weights = coef[0]
        contrib = sorted(
            zip(trained.features, feats_imp.iloc[0].values * weights),
            key=lambda x: abs(x[1]),
            reverse=True
        )[:5]
        top_txt = "; ".join([f"{k}({v:+.2f})" for k, v in contrib])

    return {
        "score": round(final, 3),
        "explanation": (
            f"Blended {alpha:.2f}*ML + {(1-alpha):.2f}*Rules. "
            f"Rule={rule:.2f}, ML={ml_prob:.2f}. "
            f"Top ML contributions: {top_txt}. "
            f"Rules rationale: {rb['explanation']}"
        ),
    }

# =========================
# 5) Smoke tests & CLI
# =========================

def _smoke_tests(alpha: float = 0.5, fetch_html: bool = False) -> dict:
    urls = {
        "nih_pmc": "https://www.ncbi.nlm.nih.gov/pmc/articles/PMC1234567/",
        "who": "https://who.int/news/item/2020-health-advisory",
        "webmd": "https://www.webmd.com/back-pain/guide/spinal-stenosis",
        "doi": "https://doi.org/10.1038/s41586-020-2649-2",
        "medium": "https://medium.com/@someone/health-tips-123",
        "http_blog": "http://example.com/blog/opinion",
    }
    trained = train_hybrid(SEED_TRAIN, fetch_html=fetch_html)
    rb = {k: evaluate_credibility(u) for k, u in urls.items()}
    hy = {k: hybrid_score(u, alpha=alpha, trained=trained, fetch_html=fetch_html) for k, u in urls.items()}

    # bounds checks
    for d in (rb, hy):
        for r in d.values():
            assert "score" in r and "explanation" in r
            assert 0.0 <= float(r["score"]) <= 1.0

    return {"rules": rb, "hybrid": hy}

def _parse_args(argv=None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Hybrid Credibility Scorer (Rules + Light ML, Adaptive CV)")
    parser.add_argument("--url", type=str, help="URL to score (hybrid). If omitted, runs --smoke.")
    parser.add_argument("--alpha", type=float, default=0.5, help="Blend weight for ML (0..1).")
    parser.add_argument("--fetch-html", action="store_true", help="Enable content features (requires requests+bs4).")
    parser.add_argument("--smoke", action="store_true", help="Run smoke tests.")
    parser.add_argument("--json-out", type=str, help="Save result(s) to this JSON path.")
    if argv is None:
        argv = sys.argv[1:]
    args, _ = parser.parse_known_args(argv)  # tolerate Jupyter's extra args like -f kernel.json
    return args

def main(argv=None):
    args = _parse_args(argv)
    if args.smoke or not args.url:
        out = _smoke_tests(alpha=args.alpha, fetch_html=args.fetch_html)
        print(json.dumps(out, indent=2))
        if args.json_out:
            with open(args.json_out, "w", encoding="utf-8") as f:
                json.dump(out, f, indent=2)
        return

    res = hybrid_score(args.url, alpha=args.alpha, fetch_html=args.fetch_html)
    print(json.dumps(res, indent=2))
    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(res, f, indent=2)

if __name__ == "__main__":
    main()

