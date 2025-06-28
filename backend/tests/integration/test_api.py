# tests/integration/test_api.py
from fastapi.testclient import TestClient
from app.main import app
import time

client = TestClient(app)

def test_translate_manga_async_flow():
    # Étape 1 : envoi du fichier, on reçoit un task_id
    with open("tests/sample_image.jpg", "rb") as img:
        response = client.post("/translate-manga", files={"file": img})
    assert response.status_code == 202  # Accepted
    json_data = response.json()
    assert "task_id" in json_data
    task_id = json_data["task_id"]

    # Petite attente pour laisser la tâche se terminer (adapter selon la logique)
    time.sleep(1)  # ou plus si nécessaire, ou faire une boucle avec retry

    # Étape 2 : requête du résultat avec l’ID de tâche
    result_response = client.get(f"/result?id={task_id}")
    assert result_response.status_code == 200
    result_data = result_response.json()
    assert "bubbles" in result_data
    assert isinstance(result_data["bubbles"], list)
