from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_translate_manga():
    file_content = b"fake image data"
    response = client.post(
        "/translate-manga",
        files={"file": ("test.jpg", file_content, "image/jpeg")}
    )
    assert response.status_code == 200
    json_data = response.json()
    assert "bubbles" in json_data
    assert len(json_data["bubbles"]) == 1
