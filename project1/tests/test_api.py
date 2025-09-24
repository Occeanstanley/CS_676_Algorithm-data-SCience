from fastapi.testclient import TestClient
from app import app

def test_api_score():
    c = TestClient(app)
    r = c.get("/score", params={"url":"https://doi.org/10.1038/s41586-020-2649-2"})
    assert r.status_code == 200
    j = r.json()
    assert set(j.keys()) == {"score","stars","explanation"}
