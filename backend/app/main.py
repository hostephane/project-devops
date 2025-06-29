from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image
import numpy as np
import easyocr
import re
import logging
import mlflow
from mlflow.tracking import MlflowClient
from transformers import pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔁 EasyOCR : Reader chargé en cache
from functools import lru_cache
@lru_cache()
def get_reader():
    logger.info("Loading EasyOCR reader...")
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

@app.post("/translate-manga")
async def translate_manga(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image = Image.open(BytesIO(contents)).convert('RGB')
        img_array = np.array(image)

        reader = get_reader()
        results = reader.readtext(img_array)

        bubbles = []
        for (bbox, text, prob) in results:
            text = clean_text(text)
            if len(text) == 0 or prob < 0.2:
                continue
            try:
                translated = translate_japanese_to_english(text)
            except Exception as e:
                logger.warning(f"Translation failed for text '{text}': {e}")
                translated = "[Translation failed]"
            bubbles.append({
                "original_text": text,
                "translated_text": translated,
                "confidence": float(prob)
            })

        return JSONResponse(content={"bubbles": bubbles})
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return JSONResponse(content={"error": "Failed to process image"}, status_code=500)
