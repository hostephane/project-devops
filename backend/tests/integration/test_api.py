from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_translate_manga_endpoint():
    with open("tests/sample_image.jpg", "rb") as img:
        response = client.post("/translate-manga", files={"file": img})
    assert response.status_code == 200
    json_data = response.json()
    assert "bubbles" in json_data
