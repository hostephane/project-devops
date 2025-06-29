# backend/tests/unit/test_utils.py
from app.main import clean_text, translate_japanese_to_english
from unittest.mock import patch

def test_clean_text():
    text = "Hello! こんにちは、世界！#@"
    cleaned = clean_text(text)
    assert cleaned == "Hello こんにちは世界"

@patch("app.main.get_tokenizer")
@patch("app.main.get_model")
def test_translate_japanese_to_english(mock_get_model, mock_get_tokenizer):
    class DummyTokenizer:
        def __call__(self, texts, return_tensors=None, truncation=None, padding=None):
            return {"input_ids": [1, 2, 3]}
        def decode(self, tokens, skip_special_tokens=True):
            return "translated text"
    class DummyModel:
        def generate(self, **kwargs):  # accepte kwargs pour éviter l'erreur
            return [[0]]

    mock_get_tokenizer.return_value = DummyTokenizer()
    mock_get_model.return_value = DummyModel()

    translated = translate_japanese_to_english("こんにちは")
    assert translated == "translated text"

def test_clean_text_empty():
    # test que le nettoyage supprime tout si c'est que ponctuation
    assert clean_text("!!!@@@###") == ""
