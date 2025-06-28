from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
from PIL import Image
import numpy as np
from transformers import MarianMTModel, MarianTokenizer
import easyocr
import re
from functools import lru_cache
import logging
import time
import psutil
import os

# ⚠️ Déclaré en haut pour éviter les erreurs
app = FastAPI()

# Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caches pour les modèles
@lru_cache()
def get_reader():
    logger.info("📦 Chargement du modèle EasyOCR...")
    return easyocr.Reader(['ja', 'en'])

@lru_cache()
def get_tokenizer():
    logger.info("📦 Chargement du tokenizer Marian...")
    return MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ja-en")

@lru_cache()
def get_model():
    logger.info("📦 Chargement du modèle Marian...")
    return MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-ja-en")

def clean_text(text: str) -> str:
    cleaned = re.sub(r"[^\wぁ-んァ-ン一-龥\s]", "", text)
    return cleaned.strip()

def translate_japanese_to_english(text: str) -> str:
    tokenizer = get_tokenizer()
    model = get_model()
    inputs = tokenizer([text], return_tensors="pt", truncation=True, padding=True)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

def log_resources(stage: str):
    process = psutil.Process(os.getpid())
    mem = process.memory_info().rss / (1024 * 1024)  # en MB
    logger.info(f"[{stage}] RAM utilisée : {mem:.2f} MB")

@app.post("/translate-manga")
async def translate_manga(file: UploadFile = File(...)):
    logger.info("🚀 Nouvelle requête /translate-manga reçue")
    start_time = time.time()
    log_resources("Début")

    try:
        # Lecture de l'image
        contents = await file.read()
        logger.info(f"📥 Fichier reçu : {file.filename}, taille : {len(contents) / 1024:.2f} KB")

        image = Image.open(BytesIO(contents)).convert('RGB')
        img_array = np.array(image)
        logger.info("🖼️ Image convertie en tableau numpy")

        # OCR
        reader = get_reader()
        logger.info("🔍 OCR en cours...")
        results = reader.readtext(img_array)
        logger.info(f"🔍 OCR terminé, {len(results)} zones de texte détectées")

        bubbles = []
        for i, (bbox, text, prob) in enumerate(results):
            cleaned = clean_text(text)
            if len(cleaned) == 0 or prob < 0.2:
                logger.debug(f"⏩ Texte ignoré (court ou faible confiance) : '{text}' (score: {prob:.2f})")
                continue

            logger.info(f"💬 Texte détecté [{i}]: '{cleaned}' (score: {prob:.2f})")
            try:
                translated = translate_japanese_to_english(cleaned)
                logger.info(f"➡️ Traduction [{i}]: '{translated}'")
            except Exception as e:
                logger.warning(f"❌ Échec traduction [{i}] '{cleaned}': {e}")
                translated = "[Translation failed]"

            bubbles.append({
                "original_text": cleaned,
                "translated_text": translated,
                "confidence": float(prob)
            })

        duration = time.time() - start_time
        logger.info(f"✅ Traitement terminé en {duration:.2f} secondes")
        log_resources("Fin")

        return JSONResponse(content={"bubbles": bubbles})

    except Exception as e:
        logger.error(f"🔥 Erreur lors du traitement : {e}")
        return JSONResponse(content={"error": "Failed to process image"}, status_code=500)
