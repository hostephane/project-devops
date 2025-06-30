from fastapi import FastAPI, UploadFile, File, Query, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image
import numpy as np
import easyocr
import re
import logging
import time
import psutil
import os
import uuid
import asyncio

import mlflow
from mlflow.tracking import MlflowClient
from transformers import pipeline
from functools import lru_cache

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔁 EasyOCR : Reader chargé en cache
@lru_cache()
def get_reader():
    logger.info("📦 Chargement du modèle EasyOCR...")
    return easyocr.Reader(['ja', 'en'])

# 🔁 MLflow : Charger pipeline de traduction depuis DagsHub
@lru_cache()
def get_translation_pipeline():
    logger.info("Fetching translation pipeline from MLflow (DagsHub)...")

    # Config DagsHub MLflow
    mlflow.set_tracking_uri("https://dagshub.com/hostephane/ML.mlflow")
    mlflow.set_experiment("manga_ocr_translation")

    client = MlflowClient()
    experiment = client.get_experiment_by_name("manga_ocr_translation")
    runs = client.search_runs(experiment_ids=[experiment.experiment_id], order_by=["start_time DESC"])
    latest_run = runs[0]
    model_uri = f"runs:/{latest_run.info.run_id}/translation_pipeline"

    logger.info(f"Loading translation model from: {model_uri}")
    return mlflow.transformers.load_model(model_uri)

# Nettoyage du texte OCR
def clean_text(text: str) -> str:
    cleaned = re.sub(r"[^\wぁ-んァ-ン一-龥\s]", "", text)
    return cleaned.strip()

# Traduction via pipeline MLflow
def translate_japanese_to_english(text: str) -> str:
    pipeline = get_translation_pipeline()
    result = pipeline(text)
    return result[0]['translation_text']

def log_resources(stage: str):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)  # MB
    logger.info(f"[{stage}] RAM utilisée : {mem:.2f} MB")

# Stockage en mémoire des tâches (à remplacer par DB ou Redis pour production)
tasks = {}

async def process_translation(task_id: str, contents: bytes):
    try:
        image = Image.open(BytesIO(contents)).convert('RGB')
        img_array = np.array(image)
        logger.info(f"Task {task_id} : 🖼️ Image convertie en tableau numpy")

        reader = get_reader()
        logger.info(f"Task {task_id} : 🔍 OCR en cours...")
        results = reader.readtext(img_array)
        logger.info(f"Task {task_id} : 🔍 OCR terminé, {len(results)} zones de texte détectées")

        bubbles = []
        for i, (bbox, text, prob) in enumerate(results):
            cleaned = clean_text(text)
            if len(cleaned) == 0 or prob < 0.2:
                logger.debug(f"Task {task_id} : ⏩ Texte ignoré : '{text}' (score: {prob:.2f})")
                continue

            logger.info(f"Task {task_id} : 💬 Texte détecté [{i}]: '{cleaned}' (score: {prob:.2f})")
            try:
                translated = translate_japanese_to_english(cleaned)
                logger.info(f"Task {task_id} : ➡️ Traduction [{i}]: '{translated}'")
            except Exception as e:
                logger.warning(f"Task {task_id} : ❌ Échec traduction [{i}] '{cleaned}': {e}")
                translated = "[Translation failed]"

            bubbles.append({
                "original_text": cleaned,
                "translated_text": translated,
                "confidence": float(prob)
            })

        tasks[task_id]["result"] = bubbles
        tasks[task_id]["status"] = "done"
        logger.info(f"Task {task_id} : ✅ Traitement terminé")
    except Exception as e:
        logger.error(f"Task {task_id} : 🔥 Erreur lors du traitement : {e}")
        tasks[task_id]["status"] = "error"
        tasks[task_id]["error"] = str(e)

@app.post("/translate-manga")
async def translate_manga(file: UploadFile = File(...)):
    logger.info("🚀 Nouvelle requête /translate-manga reçue")
    contents = await file.read()
    task_id = str(uuid.uuid4())
    tasks[task_id] = {"status": "processing", "result": None}

    # Lancer la tâche de fond
    asyncio.create_task(process_translation(task_id, contents))

    # Retourner réponse avec code 202 Accepted
    return JSONResponse(content={"task_id": task_id}, status_code=status.HTTP_202_ACCEPTED)

@app.get("/result")
async def get_result(id: str = Query(...)):
    task = tasks.get(id)
    if not task:
        return JSONResponse(status_code=404, content={"error": "Task not found"})
    if task["status"] == "processing":
        return {"status": "processing"}
    elif task["status"] == "done":
        return {"status": "done", "bubbles": task["result"]}
    else:
        return {"status": "error", "error": task.get("error", "Unknown error")}

# Endpoint healthcheck pour Docker healthcheck
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.on_event("startup")
def warm_up_model():
    logger.info("🔥 Warm-up des modèles au démarrage")
    _ = get_reader()
    _ = get_translation_pipeline()
