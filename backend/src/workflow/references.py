from pathlib import Path
from typing import Dict
from PIL import Image
from ai_clients import generate_image_from_text
from rich.console import Console

console = Console()

def generate_reference_images(
    child_name: str,
    art,
    out_dir: Path
) -> Dict[str, Path]:
    """
    Generate separate reference images for hero, props, and environment.
    Returns dict mapping reference type to file path.
    """
    out_dir.mkdir(parents=True, exist_ok=True)

    refs = {
        "hero": out_dir / "hero.png",
        "props": out_dir / "props.png",
        "environment": out_dir / "environment.png",
    }

    prompts = {
        "hero": (
            f"Children's book illustration of '{child_name}' as the main character. "
            f"Full body, clear and central. Consistent art style: {art.style}, mood: {art.mood}, "
            f"palette: {', '.join(art.colors)}."
        ),
        "props": (
            "Children's book illustration of key playful props (like toys, backpack, or magic items). "
            f"Drawn in the same style ({art.style}), mood ({art.mood}), and palette ({', '.join(art.colors)}). "
            "Objects only, no characters."
        ),
        "environment": (
            "Children's book illustration of a general background environment "
            "(like a forest, bedroom, or school). "
            f"Style: {art.style}, mood: {art.mood}, palette: {', '.join(art.colors)}. "
            "Focus on atmosphere and setting, no characters."
        ),
    }

    for key, path in refs.items():
        if not path.exists():
            console.print(f"🖌️ Generating reference image: {key}…")
            result_path = generate_image_from_text(prompts[key], path)
            if not result_path:
                console.print(f"⚠️ Failed to generate {key}, creating placeholder.")
                Image.new("RGBA", (1024, 1024), (240, 240, 240, 255)).save(path)

    return refs
