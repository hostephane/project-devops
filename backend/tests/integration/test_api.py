# backend/tests/integration/test_api.py
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

# --- Tests pour /translate-manga ---

def test_translate_manga_async_flow():
    with open("tests/sample_image.jpg", "rb") as img:
        response = client.post("/translate-manga", files={"file": img})
    assert response.status_code == 202
    json_data = response.json()
    assert "task_id" in json_data
    task_id = json_data["task_id"]

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

def test_translate_manga_bad_request():
    response = client.post("/translate-manga", files={"file": ("empty.txt", b"")})
    assert response.status_code in [202, 400, 422]

def test_translate_manga_missing_file():
    # Pas de fichier envoyé
    response = client.post("/translate-manga", files={})
    assert response.status_code in [400, 422]

# --- Tests pour /result ---

def test_result_unknown_task():
    response = client.get("/result?id=unknown-task-id")
    assert response.status_code == 404
    assert response.json()["error"] == "Task not found"

def test_result_missing_id():
    # Appel sans paramètre id
    response = client.get("/result")
    # Selon ta route, ça peut être 400 ou autre
    assert response.status_code in [400, 422]

def test_result_in_progress_task(monkeypatch):
    # Patch pour simuler tâche en cours
    monkeypatch.setattr("app.main.get_task_status", lambda task_id: {"status": "in_progress"})
    response = client.get("/result?id=test-task")
    assert response.status_code == 200
    assert response.json().get("status") == "in_progress"
