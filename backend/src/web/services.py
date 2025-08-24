import os
from pathlib import Path
from fastapi import HTTPException
from workflow.user_input import UserConfig, validate_user_config, PAINTINGS
from workflow.art_features import extract_art_features
from workflow.story import create_outline, write_full_story
from workflow.images import prompts_for_chapters, render_images
from workflow.layout import build_kids_pdf
from ai_clients import load_fallback_json
from workflow.references import generate_reference_images

OUTPUT_DIR = Path(os.getenv("OUTPUT_DIR", "output"))
FALLBACK_JSON = Path("fallback/fallback_data.json")

async def generate_book_service(req) -> str:
    print("\n--- [START] Received new book generation request ---")
    print(f"Request details: {req}")

    try:
        if req.fallback:
            # ... (la logique du fallback reste la même) ...
            return f"/download/{pdf_path.name}"

        if req.painting_id not in PAINTINGS:
            raise HTTPException(status_code=400, detail="Invalid painting_id")

        cfg = UserConfig(req.painting_id, req.child_name, req.child_age, req.family_value)
        validate_user_config(cfg)
        print(f"--- [OK] User config validated for child: {cfg.child_name}")

        painting_name = PAINTINGS[cfg.painting_id]
        
        print("--- [STEP 1/6] Extracting art features...")
        art = extract_art_features(painting_name)
        print("--- [OK] Art features extracted.")

        print("--- [STEP 2/6] Creating story outline...")
        # On récupère maintenant l'outline qui inclut le book_title
        outline = create_outline(cfg.child_name, cfg.child_age, cfg.family_value, painting_name)
        book_title_from_outline = outline.get("book_title", f"{cfg.child_name}'s Amazing Story") # Récupère le titre généré
        print(f"--- [OK] Story outline created. Book Title: '{book_title_from_outline}'")

        print("--- [STEP 3/6] Writing full story...")
        chapters = write_full_story(outline, cfg.child_age, art)
        print(f"--- [OK] Full story with {len(chapters)} chapters written.")

        print("--- [STEP 4/6] Generating reference images (hero, props, env)...")
        refs_dir = OUTPUT_DIR / "references" / cfg.child_name.lower()
        refs = generate_reference_images(cfg.child_name, art, refs_dir)
        print("--- [OK] Reference images generated.")

        print("--- [STEP 5/6] Generating chapter images...")
        prompts = prompts_for_chapters(cfg.child_name, art, outline)
        img_dir = OUTPUT_DIR / "images" / cfg.child_name.lower()
        images = render_images(prompts, img_dir, refs=refs)
        print(f"--- [OK] {len(images)} chapter images generated.")
        
        if not images or len(images) < len(chapters) + 2: # Need cover, chapters, back
             raise ValueError("Image generation failed to produce enough images for the book.")

        print("--- [STEP 6/6] Assembling the PDF book...")
        pdf_path = OUTPUT_DIR / f"book_{cfg.child_name}_api.pdf"
        build_kids_pdf(book_title_from_outline, chapters, images, pdf_path)
        print(f"--- [SUCCESS] PDF book with title '{book_title_from_outline}' created at: {pdf_path.name}")

        
        return f"/download/{pdf_path.name}"

    except Exception as e:
        print(f"\n\n--- [CRITICAL ERROR] An exception occurred during book generation! ---")
        print(f"Error Type: {type(e)}")
        print(f"Error Details: {e}")
        import traceback
        traceback.print_exc()
        print("-------------------------------------------------------------------\n\n")
        # Renvoyer une erreur claire au frontend
        raise HTTPException(status_code=500, detail=f"An internal error occurred: {e}")