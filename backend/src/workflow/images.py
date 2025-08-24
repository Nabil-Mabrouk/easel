from pathlib import Path
from typing import List, Dict, Optional
from ai_clients import generate_image_from_text, generate_image_from_images
from PIL import Image
from rich.console import Console

console = Console()

NEGATIVE_PROMPT = "--- DO NOT include any text, letters, numbers, words, or signatures in the image."

def prompts_for_chapters(child_name: str, art, outline: Dict, refs: dict = None) -> List[str]:
    """
    Builds richer, more artistic prompts for all book pages.
    """
    # --- AMÉLIORATION : Mots-clés de style pour un rendu "livre pour enfants" ---
    # Ces mots-clés seront ajoutés à chaque prompt pour guider le style visuel.
    CORE_STYLE_KEYWORDS = "charming children's book illustration, simple shapes, soft and warm lighting, clear outlines, whimsical and magical feel"

    # --- AMÉLIORATION : Construction d'un prompt de base plus narratif ---
    # On décrit le style de manière plus naturelle.
    base_style_description = (
        f"Create a {CORE_STYLE_KEYWORDS}. The main character is a child named {child_name}. "
        f"The artistic style is inspired by {art.style}, with its {art.brushwork} brushwork. "
        f"The overall mood is {art.mood}, using a color palette of {', '.join(art.colors)}."
    )

    # --- Prompt pour la couverture (Cover) ---
    cover_prompt = (
        f"{base_style_description} "
        f"For the **Book Cover**, show {child_name} looking excited and ready for an adventure. "
        "The background should be beautiful and captivating, hinting at the story to come. "
        "The character should be the main focus of the image."
        f" {NEGATIVE_PROMPT}"
    )
    
    # --- Prompt pour la quatrième de couverture (Back Cover) ---
    back_cover_prompt = (
        f"{base_style_description} "
        "For the **Back Cover**, create a peaceful and beautiful landscape scene from the story's world. "
        "Do **not** include any characters. Include a small, memorable object from the story, like a lost star or a magic paintbrush."
    )

    # --- Prompts pour les chapitres ---
    chapter_prompts = []
    chapters = outline.get("chapters", [])
    for i, chapter in enumerate(chapters, start=1):
        # Le résumé du chapitre devient l'instruction principale
        scene_description = chapter['summary']
        
        prompt = (
            f"{base_style_description} "
            f"For **Chapter {i}**, illustrate this scene: '{scene_description}'. "
            f"Show {child_name} as the central figure, actively participating in the scene. "
            "Ensure the character's appearance is consistent with previous images."
            f" {NEGATIVE_PROMPT}"
        )
        chapter_prompts.append(prompt)

    # Retourne la liste complète et ordonnée des prompts
    return [cover_prompt] + chapter_prompts + [back_cover_prompt]


def render_images(
    prompts: List[str],
    out_dir: Path,
    refs: Optional[Dict[str, Path]] = None
) -> List[Path]:
    """
    Renders images for all provided prompts (cover, chapters, back cover).
    """
    paths = []
    out_dir.mkdir(parents=True, exist_ok=True)

    ref_images = []
    if refs:
        hero_ref = refs.get("hero")
        if hero_ref and hero_ref.exists():
            ref_images.append(hero_ref)
        
        props_ref = refs.get("props")
        if props_ref and props_ref.exists():
            ref_images.append(props_ref)
            
        env_ref = refs.get("environment")
        if env_ref and env_ref.exists():
            ref_images.append(env_ref)

    for i, prompt in enumerate(prompts, start=1):
        out_path = out_dir / f"scene_{i:02d}.png"
        try:
            if ref_images:
                console.print(f"🖌️ Generating page image {i}/{len(prompts)} using I2I with {len(ref_images)} references…")
                img_path = generate_image_from_images(prompt, ref_images, out_path)
            else:
                console.print(f"🖌️ Generating page image {i}/{len(prompts)} from text prompt…")
                img_path = generate_image_from_text(prompt, out_path)

            if not img_path or not Path(img_path).exists():
                console.print(f"⚠️ Failed to generate page {i}, creating placeholder…")
                Image.new("RGB", (1024, 1024), (240, 240, 240)).save(out_path)
                img_path = out_path

            paths.append(Path(img_path))

        except Exception as e:
            console.print(f"[red]Error generating page image {i}: {e}[/red]")
            Image.new("RGB", (1024, 1024), (240, 240, 240)).save(out_path)
            paths.append(out_path)

    return paths