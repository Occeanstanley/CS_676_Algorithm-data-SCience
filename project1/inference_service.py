# inference_service.py — Final Version (Hybrid Credibility Scoring + Clean UI)
import re, random, requests
from urllib.parse import urlparse

def score_url(url: str, alpha: float = 0.5, fetch_html: bool = False):
    """
    Compute a hybrid credibility score for a given URL using improved rule weighting,
    simulated ML, and a clean, user-friendly explanation.
    """
    parsed = urlparse(url)
    domain = parsed.netloc.lower()

    rule_score = 0.0
    explanations = []
    domain_category = "Unrecognized / Generic"
    domain_confidence = "Low"

    # ──────────────── Domain Reputation ────────────────
    reputable_sources = {
        "who.int": "Global Health Organization",
        "cdc.gov": "U.S. Government Health Agency",
        "nytimes.com": "Major News Publisher",
        "bbc.com": "International News Network",
        "reuters.com": "Verified News Agency",
        "nature.com": "Peer-Reviewed Scientific Journal",
        "mayoclinic.org": "Health Institution",
        "harvard.edu": "Academic Institution",
        "stanford.edu": "Academic Institution",
        "nih.gov": "Government Research Agency"
    }

    for key, cat in reputable_sources.items():
        if key in domain:
            domain_category = cat
            domain_confidence = "High"
            rule_score += 0.7
            explanations.append(f"reputable_domain(+0.70)")
            break
    else:
        if ".gov" in domain or ".edu" in domain:
            domain_category = "Government / Educational"
            domain_confidence = "High"
            rule_score += 0.6
            explanations.append("trusted_tld(+0.60)")
        elif ".org" in domain:
            domain_category = "Nonprofit / Organization"
            domain_confidence = "Medium"
            rule_score += 0.5
            explanations.append("organization_domain(+0.50)")
        else:
            domain_category = "Generic / Commercial"
            domain_confidence = "Low"
            rule_score += 0.3
            explanations.append("generic_domain(+0.30)")

    # ──────────────── HTTPS Security ────────────────
    if url.startswith("https://"):
        rule_score += 0.1
        explanations.append("https_enabled(+0.10)")
    else:
        explanations.append("insecure_http(+0.00)")

    # ──────────────── Content Features ────────────────
    if fetch_html:
        try:
            html = requests.get(url, timeout=3).text.lower()
            if any(k in html for k in ["research", "study", "evidence", "source", "analysis"]):
                rule_score += 0.1
                explanations.append("research_keywords(+0.10)")
            if any(k in html for k in ["advertisement", "sponsored", "buy now"]):
                rule_score -= 0.1
                explanations.append("commercial_bias(-0.10)")
        except Exception:
            explanations.append("fetch_failed(+0.00)")

    rule_score = max(0, min(1, rule_score))

    # ──────────────── Simulated ML ────────────────
    ml_base = 0.75 if domain_confidence == "High" else 0.55 if domain_confidence == "Medium" else 0.4
    ml_variation = random.uniform(-0.12, 0.12)
    ml_score = max(0, min(1, ml_base + ml_variation))
    explanations.append(f"ml_component({ml_score:.2f})")

    # ──────────────── Combine Rule + ML ────────────────
    final_score = (alpha * ml_score) + ((1 - alpha) * rule_score)
    stars = int(round(final_score * 5))

    # ──────────────── User Explanation ────────────────
    domain_breakdown = (
        f"<b>🧭 Domain Trust Breakdown:</b><br>"
        f"<span style='margin-left:10px;'>• <b>Domain:</b> {domain}</span><br>"
        f"<span style='margin-left:10px;'>• <b>Category:</b> {domain_category}</span><br>"
        f"<span style='margin-left:10px;'>• <b>Confidence:</b> {domain_confidence}</span><br>"
    )

    # 🧠 Optional Technical Details (collapsed)
    tech_details = f"""
    <details style='margin-top:6px;'>
      <summary style='cursor:pointer;color:#999;'>⚙️ Technical Details (for researchers)</summary>
      <div style='margin-left:10px;margin-top:6px;'>
        Hybrid Calculation: Blended {alpha:.2f}×ML + {(1-alpha):.2f}×Rules.<br>
        Rule={rule_score:.2f}, ML={ml_score:.2f}.<br>
        <ul style='margin-top:4px;'>
          {''.join(f"<li>{e}</li>" for e in explanations)}
        </ul>
      </div>
    </details>
    """

    explanation_text = f"{domain_breakdown}{tech_details}"

    return {
        "score": round(final_score, 3),
        "stars": stars,
        "explanation": explanation_text,
        "domain": domain,
        "category": domain_category,
        "confidence": domain_confidence
    }


# ──────────────── Colored Summary Box ────────────────
def _plain_summary(score: float, domain: str = "", category: str = "", confidence: str = "") -> str:
    """Creates a visually enhanced summary box with domain trust breakdown inside."""
    pct = round(score * 100)

    if pct < 35:
        bg, text, emoji, level, line = (
            "#ff4d4d", "white", "🔴", "Low Credibility",
            "Low confidence; consider alternative references or verify with trusted sources."
        )
    elif pct < 65:
        bg, text, emoji, level, line = (
            "#ffcc66", "black", "🟡", "Moderate Credibility",
            "May benefit from stronger citations or expert review."
        )
    else:
        bg, text, emoji, level, line = (
            "#33cc85", "white", "🟢", "High Credibility",
            "Strong signals of reliability and expert support."
        )

    domain_section = f"""
        <div style='margin-top:8px;font-size:14px;'>
            <b>🧭 Domain Trust Breakdown:</b><br>
            <span style='margin-left:10px;'>• <b>Domain:</b> {domain}</span><br>
            <span style='margin-left:10px;'>• <b>Category:</b> {category or 'Unknown'}</span><br>
            <span style='margin-left:10px;'>• <b>Confidence:</b> {confidence or 'N/A'}</span>
        </div>
    """

    return f"""
    <div style="background:{bg};color:{text};padding:14px;border-radius:10px;margin-top:10px;
                font-size:15px;line-height:1.5;box-shadow:0 2px 4px rgba(0,0,0,0.2);">
        <b>{emoji} {level} ({pct}%)</b><br>
        {line}
        {domain_section}
    </div>
    """
