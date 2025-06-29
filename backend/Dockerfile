FROM python:3.12-slim as builder

RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx curl build-essential ca-certificates clang pkg-config libssl-dev && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Installer rustup (pas rustc via apt)
RUN curl https://sh.rustup.rs -sSf | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Forcer Rust stable 1.70.0
RUN rustup install 1.70.0
RUN rustup default 1.70.0

# Mettre à jour pip/setuptools/wheel
RUN pip install --upgrade pip setuptools wheel

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Nettoyer caches
RUN rm -rf /root/.cache/pip /root/.cargo/registry

RUN python -c "\
import easyocr; easyocr.Reader(['ja', 'en']); \
from transformers import MarianMTModel, MarianTokenizer; \
MarianTokenizer.from_pretrained('Helsinki-NLP/opus-mt-ja-en'); \
MarianMTModel.from_pretrained('Helsinki-NLP/opus-mt-ja-en')"

COPY . .

FROM python:3.12-slim

RUN apt-get update && apt-get install -y \
    libglib2.0-0 libsm6 libxrender1 libxext6 libgl1-mesa-glx curl && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY --from=builder /usr/local/bin /usr/local/bin
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /app /app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
