# CS_676_Algorithm-data-Science

## Project 1 – Credibility Scoring System

**Author:** Stanley Occean  
**Course:** CS 676 – Algorithm & Data Science  
**Deliverable 2 Due:** September 26, 2025

---

## ✅ Deliverable 2 – Detailed Technique Report

### 🎯 Objective
This deliverable provides an in-depth analysis and justification of the credibility scoring system developed for Project 1. The report includes algorithm rationale, literature review, model comparison, and documentation for future improvements.

---

## 1. Algorithmic Design & Rationale

I designed a hybrid scoring architecture that combines rule-based logic with logistic regression. Features include HTTPS usage, domain trust, TLD (.gov, .edu), DOI patterns, and optional content indicators.

### 1.1 Feature Selection
- Structural: HTTPS, short domain, TLD
- Reputational: presence of known trusted domains (NIH, WHO, etc.)
- Semantic: blog indicators, DOI-like path
- Optional content features (if HTML fetch is enabled): citation density, article length, readability

### 1.2 Scoring Mechanism
- **Rule-Based Score:** additive scoring based on heuristics; bounded between 0 and 1.
- **ML Score:** trained logistic regression model with Platt-calibrated probabilities.
- **Final Hybrid Score:**  
  `hybrid_score = α * ML + (1 - α) * Rule`  
  (where alpha is a configurable blending parameter, default 0.5)

### 1.3 Reproducibility & Scalability
- Stateless inference with no database requirement
- All components run offline except optional content fetch
- Small ML footprint: fast, low-memory model (LogisticRegression)
- Deterministic seed + JSON I/O = reproducible and auditable

---

## 2. Literature Review

### 2.1 Academic Foundations
- "Fake News Detection Using Machine Learning" (Zhou et al., 2019) → supports hybrid designs
- "Platt Scaling for Calibrated Probabilities" → basis for using `CalibratedClassifierCV`
- "Trust and Credibility in Online Health Info" → validated our features like HTTPS, .gov/.edu

### 2.2 Industry Techniques
- **Google E-E-A-T**: domain & author quality rating
- **NewsGuard, MBFC**: human-vetted credibility lists
- **OpenPageRank**: indirect reputational signals

### 2.3 Gaps in Prior Art
- Many academic models are black-box and non-interpretable
- Industry solutions lack transparent scoring logic
- Little support for real-time, lightweight scoring

### 2.4 Our Contribution
- Fully interpretable rule-based layer
- Simple ML model with explanations
- Offline-first, JSON-in/out format
- Ideal for chatbot, CMS, and education use

---

## 3. Justification & Comparison

### 3.1 Why Hybrid?
- Rule-only: easy to explain, but rigid
- ML-only: flexible, but less transparent
- Hybrid: interpretable AND adaptive

### 3.2 Trade-Offs Summary

| Approach      | Accuracy | Interpretability | Offline | API-Ready |
|---------------|----------|------------------|---------|-----------|
| Rule-Based    | Moderate | High             | ✅      | ✅        |
| ML-Only       | Higher   | Low              | ❌      | ✅        |
| **Hybrid**    | ✅ Best   | ✅ High           | ✅      | ✅        |

### 3.3 Empirical Validation
- Smoke test scores range from 0.20 (blog) to 0.85 (NIH)
- Hybrid score aligns closely with human expectations
- Calibrated probabilities ensure reliability for thresholds

---

## 4. Documentation & Future Refinement

### 4.1 API Input/Output

```json
Input: {
  "url": "https://example.com/article",
  "alpha": 0.5,
  "fetch_html": false
}

Output: {
  "score": 0.67,
  "explanation": "Blended 0.50*ML + 0.50*Rules. Rule=0.60, ML=0.73. Top ML features: https(+0.45); reputable(+0.40)..."
}
```

### 4.2 Tunable Parameters

| Parameter     | Description                                      | Default |
|---------------|--------------------------------------------------|---------|
| `alpha`       | Weight of ML score vs. rule score                | 0.5     |
| `fetch_html`  | Enables content-based features                   | false   |
| `cv_folds`    | Adaptive based on dataset class count            | auto    |

### 4.3 Roadmap

- Add NLP-based features (bias, tone, sentiment)
- Better calibration using larger labeled dataset
- Dashboard for monitoring score drift
- Enable citation extraction and context-aware scoring
- Open-sourcing + community evaluation

---

## ✅ Conclusion

This credibility scoring model achieves the key goal of providing transparent, trustworthy, and adaptive scoring of online information sources. It balances interpretability and flexibility through a hybrid ML + rules approach and is well-positioned for extension into real-world applications.
