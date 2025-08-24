import argparse
import os
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from workflow.user_input import UserConfig, validate_user_config, PAINTINGS
from workflow.art_features import extract_art_features
from workflow.story import create_outline, write_full_story
from workflow.images import prompts_for_chapters, render_images
from workflow.layout import build_kids_pdf
from workflow.references import generate_reference_images
from ai_clients import load_fallback_json
from workflow.memory import MemoryStore

# ------------------- Paths -------------------
MEMORY_PATH = Path("output/memory.json")
memory = MemoryStore(MEMORY_PATH)
OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
FALLBACK_JSON = Path("fallback/fallback_data.json")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

console = Console()


# ------------------- Full Run -------------------
def run_full(cfg: UserConfig):
    validate_user_config(cfg)
    painting_name = PAINTINGS[cfg.painting_id]

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=False,
    ) as progress:
        # --- Step 1: Art features ---
        t1 = progress.add_task("Extracting art features…", total=1)
        art = extract_art_features(painting_name)
        progress.update(t1, completed=1)
        progress.stop_task(t1)

        # --- Step 2: Create outline ---
        t2 = progress.add_task("Creating outline…", total=1)
        outline = create_outline(cfg.child_name, cfg.child_age, cfg.family_value, painting_name)
        progress.update(t2, completed=1)
        progress.stop_task(t2)

        # --- Step 3: Write chapters ---
        t3 = progress.add_task("Writing chapters…", total=1)
        chapters = write_full_story(outline, cfg.child_age, art) 
        progress.update(t3, completed=1)
        progress.stop_task(t3)

        # --- Step 4: Generate reference images ---
        t4 = progress.add_task("Generating reference images…", total=1)
        refs_dir = OUTPUT_DIR / "references" / cfg.child_name.lower()
        refs = generate_reference_images(cfg.child_name, art, refs_dir)
        progress.update(t4, completed=1)
        progress.stop_task(t4)

        # --- Step 5: Generate chapter images ---
        t5 = progress.add_task("Generating chapter images…", total=1)
        prompts = prompts_for_chapters(cfg.child_name, art, outline)
        img_dir = OUTPUT_DIR / "images" / cfg.child_name.lower()

        # Pass references to render_images
        images = render_images(prompts, img_dir, refs=refs)
        progress.update(t5, completed=1)
        progress.stop_task(t5)

        # --- Step 6: Compose PDF ---
        t6 = progress.add_task("Composing PDF…", total=1)
        pdf_path = OUTPUT_DIR / f"book_{cfg.child_name}.pdf"
            # !!! UTILISE LE TITRE DE L'OUTLINE ICI !!!
        book_title = outline.get("book_title", f"{cfg.child_name}'s Amazing Story")
        build_kids_pdf(book_title, chapters, images, pdf_path)
        progress.update(t6, completed=1)
        progress.stop_task(t6)

    console.print(f"[bold green]Done.[/bold green] PDF: {pdf_path}")

    # Save session
    memory.put_session({
        "child_name": cfg.child_name,
        "painting": painting_name,
        "outline": outline,
        "chapters": chapters,
        "images": [str(p) for p in images],
        "pdf": str(pdf_path)
    })
    return pdf_path


# ------------------- Fallback Run -------------------
def run_fallback():
    data = load_fallback_json(FALLBACK_JSON)
    chapters = data["chapters"]
    images = [Path(p) for p in data["images"]]
    pdf_path = OUTPUT_DIR / "book_fallback.pdf"
    build_kids_pdf(data["title"], chapters, images, pdf_path)
    console.print(f"[bold green]Done (fallback).[/bold green] PDF: {pdf_path}")
    return pdf_path


# ------------------- CLI -------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="KidsBookAI — Generate a personalized kids' book.")
    parser.add_argument("--painting", default="starry_night", choices=list(PAINTINGS.keys()))
    parser.add_argument("--name", default="Emma")
    parser.add_argument("--age", type=int, default=6)
    parser.add_argument("--value", default="sharing")
    parser.add_argument("--fallback", action="store_true", help="Use pre-generated fallback JSON + images.")
    args = parser.parse_args()

    if args.fallback:
        run_fallback()
    else:
        cfg = UserConfig(args.painting, args.name, args.age, args.value)
        run_full(cfg)
