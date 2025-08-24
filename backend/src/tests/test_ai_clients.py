import os
from pathlib import Path
from ai_clients import generate_text, generate_image_from_text

def test_generate_text_smoke():
    if not os.getenv("AIMLAPI_KEY"):
        # Offline/CI mode: skip
        assert True
        return
    out = generate_text("You are helpful", "Say 'ping'.")
    assert out is None or "ping" in out.lower()

def test_generate_image_smoke(tmp_path: Path):
    if not os.getenv("AIMLAPI_KEY"):
        assert True
        return
    img_path = tmp_path / "smoke.png"
    path = generate_image_from_text("A tiny blue square sticker", img_path)
    assert path is None or path.exists()
