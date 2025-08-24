from typing import Dict, List, Any, Optional
from ai_clients import generate_json, generate_text
from workflow.art_features import ArtFeatures
from rich.console import Console

console = Console()

def create_outline(child_name: str, age: int, value: str, painting: str) -> Dict:
    """
    Generates a 3-chapter outline with titles (≤3 words) and summaries (≤20 words),
    including some intrigue, funny situations, and hooks for a kids' story.
    """
    sys_prompt = (
        "Return JSON: {hero: {name, traits}, chapters:[{title, summary}], book_title: str}. "
        "Titles ≤4 words, summaries ≤20 words. Make it imaginative, funny, and engaging."
    )
    user_prompt = (
        f"Create a 3-chapter outline for a children's picture book inspired by {painting}. "
        f"Hero: {child_name}, Age: {age}, Family value: {value}. "
        "Include playful situations, surprises, and curiosity-driven story arcs."
        "Also, suggest a short, catchy book title (max 5 words)."
    )

    data = generate_json(sys_prompt, user_prompt)
    if not data:
        # --- Fallback outline ---
        data = {
            "hero": {"name": child_name, "traits": ["curious", "kind"]},
            "chapters": [
                {"title": f"Adventure {i+1}", "summary": f"{child_name} learns about {value}."}
                for i in range(6)
            ]
        }

    # --- Enforce title + summary limits ---
    for ch in data.get("chapters", []):
        # Title ≤ 5 words
        words = ch["title"].split()
        if len(words) > 5:
            ch["title"] = " ".join(words[:5])

        # Summary ≤ 20 words
        words = ch["summary"].split()
        if len(words) > 20:
            ch["summary"] = " ".join(words[:20]) + "..."
    
    # Assurer que le book_title est aussi limité si l'IA devient trop bavarde
    if "book_title" in data:
        title_words = data["book_title"].split()
        if len(title_words) > 7:
            data["book_title"] = " ".join(title_words[:7]) + "..."

    return data


def write_full_story(outline: Dict, age: int, art_features: ArtFeatures) -> List[str]:
    """
    Generate the full story in one LLM call to ensure narrative consistency.
    Returns a list of chapter texts, in order.
    """
    chapters = outline.get("chapters", [])
    chapter_titles = [ch["title"] for ch in chapters]
    chapter_summaries = [ch["summary"] for ch in chapters]

    # --- System prompt ---
    sys_prompt = (
        "You are a skilled children's book writer. "
        "Write a playful, imaginative story for ages 4–7. "
        "Maintain the hero's personality and traits consistently across all chapters. "
        "Ensure continuity, recurring motifs, humor, and curiosity-driven surprises. "
        "Return JSON: {chapters:[{title, text}]}, each text ≤20 words."
    )

    # --- User prompt ---
    user_prompt = (
        f"Hero traits: {outline['hero']}\n"
        f"Art references: hero={art_features.hero_path}, props={art_features.prop_paths}, background={art_features.background_path}\n"
        f"Art style hints: colors={art_features.colors}, mood={art_features.mood}, "
        f"style={art_features.style}, brushwork={art_features.brushwork}\n"
        f"Target age: {age}\n"
        "Chapter outline:\n"
    )

    for i, (title, summary) in enumerate(zip(chapter_titles, chapter_summaries), start=1):
        user_prompt += f"{i}. Title: {title}, Summary: {summary}\n"

    user_prompt += "Write the full story as per the outline, keeping the hero, props, and mood consistent. Return JSON."

    # --- Generate JSON from LLM ---
    data: Optional[Dict[str, Any]] = generate_json(sys_prompt, user_prompt)
    if not data:
        console.print("[yellow]⚠️ Story generation failed, using fallback text.[/yellow]")
        return [f"{ch['title']}: {ch['summary']}" for ch in chapters]

    # --- Extract chapter texts safely ---
    chapter_texts = []
    for ch in data.get("chapters", []):
        text = ch.get("text") or ch.get("summary") or ch.get("title")
        # Safeguard: limit to 20 words
        words = text.split()
        if len(words) > 20:
            text = " ".join(words[:20]) + "..."
        chapter_texts.append(text)

    return chapter_texts



def write_chapters(outline: Dict, age: int, art_features: ArtFeatures) -> List[str]:
    """
    Expands each chapter to a short story (≤20 words),
    ensuring character consistency and using reference hero/props hints for imagery.
    """
    chapters = []
    for ch in outline["chapters"]:
        sys_prompt = (
            "Write a playful, short children's story scene. "
            "Limit: ≤20 words. "
            "Keep the same hero personality and traits across chapters. "
            "Make it imaginative, curious, and funny—like classic picture books. "
            "Each chapter should feel like a tiny adventure with a magical or silly surprise. "
            "Age-appropriate for 4–7 year olds."
        )


        # Include reference images prompts for consistency
        user_prompt = (
            f"Chapter title: {ch['title']}\n"
            f"Summary: {ch['summary']}\n"
            f"Hero traits: {outline['hero']}\n"
            f"Hero reference image: {art_features.hero_path}\n"
            f"Props reference images: {art_features.prop_paths}\n"
            f"Background reference image: {art_features.background_path}\n"
            f"Art style hints: colors={art_features.colors}, mood={art_features.mood}, "
            f"style={art_features.style}, brushwork={art_features.brushwork}\n"
            f"Target reading age: {age}\n"
            "Write final text ≤20 words."
        )

        text = generate_text(sys_prompt, user_prompt) or f"{ch['title']}: {ch['summary']}"
        # Safeguard
        words = text.split()
        if len(words) > 20:
            text = " ".join(words[:20]) + "..."
        chapters.append(text)

    return chapters
