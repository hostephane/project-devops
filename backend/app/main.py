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

app = FastAPI()

# Middleware CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://earnest-enjoyment-production.up.railway.app"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Caches pour les modèles
@lru_cache()
def get_reader():
    return easyocr.Reader(['ja', 'en'])

@lru_cache()
def get_tokenizer():
    return MarianTokenizer.from_pretrained("Helsinki-NLP/opus-mt-ja-en")

@lru_cache()
def get_model():
    return MarianMTModel.from_pretrained("Helsinki-NLP/opus-mt-ja-en")

def clean_text(text: str) -> str:
    return re.sub(r"[^\wぁ-んァ-ン一-龥\s]", "", text).strip()

def translate_japanese_to_english(text: str) -> str:
    tokenizer = get_tokenizer()
    model = get_model()
    inputs = tokenizer([text], return_tensors="pt", truncation=True, padding=True)
    translated = model.generate(**inputs)
    return tokenizer.decode(translated[0], skip_special_tokens=True)

@app.post("/translate-manga")
async def translate_manga(file: UploadFile = File(...)):
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
        except Exception:
            translated = "[Translation failed]"
        bubbles.append({
            "original_text": text,
            "translated_text": translated,
            "confidence": float(prob)
        })

    return JSONResponse(content={"bubbles": bubbles})
