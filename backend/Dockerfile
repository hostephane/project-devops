FROM python:3.12-slim

WORKDIR /app

# Copier requirements depuis backend
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copier le contenu complet du backend
COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
