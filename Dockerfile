FROM python:3.12-slim

# Installer les dépendances système minimales (sinon easyocr/PIL plante)
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier les dépendances
COPY backend/requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# === Pré-téléchargement des modèles ===
RUN python -c "import easyocr; easyocr.Reader(['ja', 'en'])"
RUN python -c "from transformers import MarianMTModel, MarianTokenizer; \
    MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-ja-en'); \
    MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-ja-en')"

# Copier le backend complet
COPY backend/ .

# Lancer le serveur FastAPI via uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
