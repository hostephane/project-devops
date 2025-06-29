FROM python:3.12-slim

# Dépendances système pour easyocr/pillow
RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier requirements depuis backend
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

# Copier le backend
COPY . .

# Exposer le port de l'API
EXPOSE 8000

# Lancer FastAPI avec Uvicorn
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
