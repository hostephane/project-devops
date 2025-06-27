from fastapi import FastAPI, UploadFile, File
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import easyocr
from io import BytesIO
from PIL import Image
import numpy as np
from transformers import MarianMTModel, MarianTokenizer
import re

# Initialisation de l'application FastAPI
app = FastAPI()

# Middleware CORS pour autoriser le frontend à se connecter
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # pour le dev local
        "https://ton-frontend.railway.app"  # à adapter selon ton domaine de déploiement
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Chargement du modèle OCR (EasyOCR)
reader = easyocr.Reader(['ja', 'en'])

# Chargement du modèle de traduction japonais → anglais
model_name = "Helsinki-NLP/opus-mt-ja-en"
tokenizer = MarianTokenizer.from_pretrained(model_name)
model = MarianMTModel.from_pretrained(model_name)

# Fonction de nettoyage de texte (on garde japonais, alpha-num et espace)
def clean_text(text: str) -> str:
    cleaned = re.sub(r"[^\wぁ-んァ-ン一-龥\s]", "", text)
    return cleaned.strip()

# Fonction de traduction jap → anglais
def translate_japanese_to_english(text: str) -> str:
    inputs = tokenizer([text], return_tensors="pt", truncation=True, padding=True)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

# Endpoint POST pour envoyer une image manga et récupérer la traduction
@app.post("/translate-manga")
async def translate_manga(file: UploadFile = File(...)):
    contents = await file.read()
    image = Image.open(BytesIO(contents)).convert('RGB')
    img_array = np.array(image)

    results = reader.readtext(img_array)

    bubbles = []
    for (bbox, text, prob) in results:
        text = clean_text(text)
        if len(text) == 0 or prob < 0.2:
            continue
        try:
            translated = translate_japanese_to_english(text)
        except Exception:
            translated = "[Translation failed]"
        bubbles.append({
            "original_text": text,
            "translated_text": translated,
            "confidence": float(prob)
        })

    return JSONResponse(content={"bubbles": bubbles})
