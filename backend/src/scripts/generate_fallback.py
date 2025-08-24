import json
from pathlib import Path
import sys

# Add parent (src/) to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from ai_clients import generate_text, generate_image_from_text, console
from PIL import Image, ImageDraw

def main():
    # --- Intro Banner ---
    console.rule("[bold magenta]Easel Storybook Generator – Fallback Builder[/bold magenta]")
    console.print(
        "[cyan]This script creates a [bold]fallback dataset[/bold] for the storybook generator.\n"
        "It generates local images + text to test PDF layout without live AI API calls.[/cyan]\n"
    )

    fb_dir = Path("fallback")
    fb_dir.mkdir(exist_ok=True)

    title = "Emma and the Starry Night"

    # --- Step 1: Generate fallback text ---
    console.rule("[bold cyan] Step 1: Generating fallback text")
    chapters = []
    try:
        for i, prompt in enumerate([
            "Write a 50-word chapter: Emma dreams under starry skies about sharing.",
            "Write a 50-word chapter: Emma learns to share stardust with friends."
        ], start=1):
            console.print(f"📖 Generating Chapter {i}...")
            ch = generate_text("You write for kids.", prompt)
            if ch:
                console.print(f"✅ Chapter {i} generated.")
            else:
                console.print(f"❌ Chapter {i} failed, using placeholder text.")
                ch = f"Draft chapter {i}"
            chapters.append(ch)
    except Exception as e:
        console.print(f"[red]Error generating text: {e}[/red]")
        chapters = ["Draft chapter 1", "Draft chapter 2"]

    # --- Step 2: Generate fallback images ---
    console.rule("[bold cyan] Step 2: Generating fallback images")
    image_prompts = [
        "Cover: Child under swirling starry night, magical, warm colors",
        "Scene 1: Child walking under starry sky, friendly glow",
        "Scene 2: Sharing stardust with friends, gentle night lights",
        "Scene 3: Emma discovering hidden stars, calm and wonder",
        "Back cover: Starry sky with moon and clouds, peaceful"
    ]
    images = []

    for i, prompt in enumerate(image_prompts, start=1):
        img_path = fb_dir / f"fallback_img_{i}.png"
        console.print(f"🖼️ Generating Image {i}...")
        img = generate_image_from_text(prompt, img_path)
        if img:
            console.print(f"✅ Image {i} generated. Size: {Image.open(img).size}")
            images.append(str(img))
        else:
            console.print(f"❌ Image {i} failed, creating placeholder.")
            # Create placeholder
            placeholder = fb_dir / f"placeholder_{i}.png"
            img_obj = Image.new("RGB", (1024, 1024), color=(230, 230, 230))
            d = ImageDraw.Draw(img_obj)
            d.text((40, 40), f"Fallback Placeholder {i}", fill=(20,20,20))
            img_obj.save(placeholder)
            images.append(str(placeholder))
            console.print(f"🖼️ Placeholder saved: {placeholder}")

    # --- Step 3: Save fallback JSON ---
    data = {"title": title, "chapters": chapters, "images": images}
    with open(fb_dir / "fallback_data.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    console.rule("[bold green]✅ Fallback Generated")
    console.print(f"📂 Files saved under: [bold]{fb_dir}[/bold]\n")

    # --- Next Steps ---
    console.rule("[bold yellow]🚀 Next Steps")
    console.print(
        "Now that fallback content is generated, you can test the pipeline without AI calls:\n\n"
        "1️⃣ Run kidsbook.py with the fallback JSON:\n"
        "   [green]python kidsbook.py --fallback[/green]\n\n"
        "2️⃣ Verify PDF generation works with local text + images.\n"
        "   (Check layout, fonts, page breaks, etc.)\n\n"
        "3️⃣ Once layout is stable, re-enable live API calls in kidsbook.py\n"
        "   by providing your AIML API key in [.env].\n"
    )


if __name__ == "__main__":
    main()
