from app.main import clean_text

def test_clean_text():
    text = "Hello! こんにちは、世界！#@"
    cleaned = clean_text(text)
    assert cleaned == "Hello こんにちは世界"
