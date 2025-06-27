FROM python:3.12-slim

# Installer les dépendances système
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier et installer les dépendances
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Pré-télécharger les modèles
RUN python -c "\
import easyocr; easyocr.Reader(['ja', 'en']); \
from transformers import MarianMTModel, MarianTokenizer; \
MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-ja-en'); \
MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-ja-en')"

# Copier le code backend
COPY . .

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
