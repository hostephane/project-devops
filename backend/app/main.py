import time
import psutil
import os

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
