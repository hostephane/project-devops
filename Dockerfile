FROM python:3.12-slim

WORKDIR /app

# Copier les dépendances
COPY backend/requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# === Pré-téléchargement des modèles ===
RUN python -c "import easyocr; easyocr.Reader(['ja', 'en'])"
RUN python -c "from transformers import MarianMTModel, MarianTokenizer; \
               MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-ja-en'); \
               MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-ja-en')"

# Copier tout le backend
COPY backend/ ./backend/

WORKDIR /app/backend

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
