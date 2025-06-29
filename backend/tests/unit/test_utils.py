# backend/tests/unit/test_utils.py
from app.main import clean_text, translate_japanese_to_english
from unittest.mock import patch

# Tests pour clean_text

def test_clean_text_basic():
    text = "Hello! こんにちは、世界！#@"
    cleaned = clean_text(text)
    assert cleaned == "Hello こんにちは世界"

def test_clean_text_empty_input():
    # test que le nettoyage supprime tout si c'est que ponctuation
    assert clean_text("!!!@@@###") == ""

def test_clean_text_whitespace_only():
    # test que les espaces sont conservés
    assert clean_text("   ") == "   "


# Tests pour translate_japanese_to_english

@patch("app.main.get_tokenizer")
@patch("app.main.get_model")
def test_translate_japanese_to_english_basic(mock_get_model, mock_get_tokenizer):
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

@patch("app.main.get_tokenizer")
@patch("app.main.get_model")
def test_translate_japanese_to_english_empty_input(mock_get_model, mock_get_tokenizer):
    class DummyTokenizer:
        def __call__(self, texts, return_tensors=None, truncation=None, padding=None):
            return {"input_ids": []}
        def decode(self, tokens, skip_special_tokens=True):
            return ""
    class DummyModel:
        def generate(self, **kwargs):
            return [[]]

    mock_get_tokenizer.return_value = DummyTokenizer()
    mock_get_model.return_value = DummyModel()

    translated = translate_japanese_to_english("")
    assert translated == ""

@patch("app.main.get_tokenizer")
@patch("app.main.get_model")
def test_translate_japanese_to_english_error_handling(mock_get_model, mock_get_tokenizer):
    class DummyTokenizer:
        def __call__(self, texts, return_tensors=None, truncation=None, padding=None):
            raise Exception("tokenizer error")
        def decode(self, tokens, skip_special_tokens=True):
            return "should not reach here"
    class DummyModel:
        def generate(self, **kwargs):
            return [[0]]

    mock_get_tokenizer.return_value = DummyTokenizer()
    mock_get_model.return_value = DummyModel()

    try:
        translate_japanese_to_english("こんにちは")
        assert False, "Exception was not raised"
    except Exception as e:
        assert str(e) == "tokenizer error"
