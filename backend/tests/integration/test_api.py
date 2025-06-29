# backend/tests/integration/test_api.py
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_translate_manga_async_flow():
    # Étape 1 : upload fichier image valide
    with open("tests/sample_image.jpg", "rb") as img:
        response = client.post("/translate-manga", files={"file": img})
    assert response.status_code == 202
    json_data = response.json()
    assert "task_id" in json_data
    task_id = json_data["task_id"]

    # Polling avec timeout max 10s
    for _ in range(20):
        time.sleep(0.5)
        result_response = client.get(f"/result?id={task_id}")
        if result_response.json().get("status") == "done":
            break
    else:
        assert False, "Timeout waiting for task completion"

    result_data = result_response.json()
    assert "bubbles" in result_data
    assert isinstance(result_data["bubbles"], list)

def test_result_unknown_task():
    response = client.get("/result?id=unknown-task-id")
    assert response.status_code == 404
    assert response.json()["error"] == "Task not found"

def test_translate_manga_bad_request():
    # envoyer un fichier vide ou invalide
    response = client.post("/translate-manga", files={"file": ("empty.txt", b"")})
    # soit erreur 400 (à adapter selon backend), ici on teste juste pas 500
    assert response.status_code in [400, 422]
