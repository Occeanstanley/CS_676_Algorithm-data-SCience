from inference_service import score_url
import asyncio

def test_score_url_rules_only_runs():
    res = asyncio.run(score_url("https://www.webmd.com/back-pain/guide/spinal-stenosis",
                                alpha=0.5, fetch_html=False))
    assert 0.0 <= res["score"] <= 1.0
    assert "explanation" in res and "stars" in res
