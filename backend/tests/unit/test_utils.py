# backend/tests/unit/test_utils.py
from app.main import clean_text, translate_japanese_to_english
from unittest.mock import patch

def test_clean_text():
    text = "Hello! こんにちは、世界！#@"
    cleaned = clean_text(text)
    assert cleaned == "Hello こんにちは世界"

def test_clean_text_empty():
    assert clean_text("!!!@@@###") == ""

def test_clean_text_whitespace_only():
    assert clean_text("   ") == ""

@patch("app.main.get_translation_pipeline")
def test_translate_japanese_to_english_basic(mock_pipeline):
    mock_pipeline.return_value = lambda x: [{"translation_text": "translated text"}]
    result = translate_japanese_to_english("こんにちは")
    assert result == "translated text"

@patch("app.main.get_translation_pipeline")
def test_translate_japanese_to_english_empty_input(mock_pipeline):
    mock_pipeline.return_value = lambda x: [{"translation_text": ""}]
    result = translate_japanese_to_english("")
    assert result == ""

@patch("app.main.get_translation_pipeline")
def test_translate_japanese_to_english_error_handling(mock_pipeline):
    # simule une erreur dans le modèle
    mock_pipeline.side_effect = Exception("Mocked error")
    try:
        result = translate_japanese_to_english("テスト")
    except Exception as e:
        assert str(e) == "Mocked error"
