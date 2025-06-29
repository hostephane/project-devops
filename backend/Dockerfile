# Étape 1 : builder - construction et installation des dépendances
FROM python:3.12-slim as builder

# Installer les bibliothèques système nécessaires
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier les dépendances
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Nettoyer le cache pip
RUN rm -rf /root/.cache/pip

# Pré-télécharger les modèles pour éviter les téléchargements au runtime
RUN python -c "\
import easyocr; easyocr.Reader(['ja', 'en']); \
from transformers import MarianMTModel, MarianTokenizer; \
MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-ja-en'); \
MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-ja-en')"

# Copier tout le backend
COPY . .

# Étape 2 : image finale légère
FROM python:3.12-slim

# Installer les bibliothèques système nécessaires
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier les binaires (ex: uvicorn), les packages Python et le code
COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app /app

EXPOSE 8000

# Healthcheck avec délai de démarrage plus long (start-period=60s)
HEALTHCHECK --interval=10s --timeout=3s --start-period=60s --retries=5 \
  CMD curl --fail http://localhost:8000/health || exit 1

# Commande de lancement du backend
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
