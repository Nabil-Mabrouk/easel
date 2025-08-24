from dataclasses import dataclass, field
from typing import List, Optional
from pathlib import Path
import logging
from ai_clients import generate_json, generate_image_from_text

logger = logging.getLogger(__name__)

REF_DIR = Path("refs")
REF_DIR.mkdir(exist_ok=True)

@dataclass
class ArtFeatures:
    colors: List[str]
    mood: str
    style: str
    brushwork: str
    hero_prompt: str = ""
    prop_prompts: List[str] = field(default_factory=list)
    background_prompt: str = ""
    hero_path: Optional[Path] = None
    prop_paths: List[Path] = field(default_factory=list)
    background_path: Optional[Path] = None


FALLBACK_FEATURES = ArtFeatures(
    colors=["deep blue", "yellow", "black"],
    mood="dreamy",
    style="post-impressionism",
    brushwork="swirling, expressive",
    hero_prompt="Child, smiling, friendly, colorful outfit, kid-friendly illustration",
    prop_prompts=["magical stardust", "wand"],
    background_prompt="Starry night, dreamy, warm colors, kid-friendly illustration"
)

SYS_PROMPT = (
    "You are an expert art critic. "
    "Extract artistic features of the painting and return strictly as JSON "
    "with keys: colors(list), mood(str), style(str), brushwork(str), "
    "hero_prompt(str), prop_prompts(list), background_prompt(str)."
)

def normalize_features(raw: dict) -> ArtFeatures:
    return ArtFeatures(
        colors=raw.get("colors", []),
        mood=raw.get("mood", "unknown").strip().lower(),
        style=raw.get("style", "unspecified").strip(),
        brushwork=raw.get("brushwork", "unspecified").strip(),
        hero_prompt=raw.get("hero_prompt", FALLBACK_FEATURES.hero_prompt),
        prop_prompts=raw.get("prop_prompts", FALLBACK_FEATURES.prop_prompts),
        background_prompt=raw.get("background_prompt", FALLBACK_FEATURES.background_prompt)
    )

def extract_art_features(painting_name: str) -> ArtFeatures:
    user = f"Analyze the painting '{painting_name}' and extract its artistic features."
    raw = generate_json(SYS_PROMPT, user)

    if not raw:
        logger.warning("Falling back to default art features for %s", painting_name)
        art = FALLBACK_FEATURES
    else:
        try:
            art = normalize_features(raw)
        except Exception as e:
            logger.error("Error normalizing features for %s: %s", painting_name, e)
            art = FALLBACK_FEATURES

    # Generate reference images if missing
    if not art.hero_path:
        art.hero_path = REF_DIR / "hero.png"
        if not art.hero_path.exists():
            generate_image_from_text(art.hero_prompt, art.hero_path)

    if not art.background_path:
        art.background_path = REF_DIR / "background.png"
        if not art.background_path.exists():
            generate_image_from_text(art.background_prompt, art.background_path)

    if not art.prop_paths:
        art.prop_paths = []
        for i, prompt in enumerate(art.prop_prompts):
            p_path = REF_DIR / f"prop_{i}.png"
            if not p_path.exists():
                generate_image_from_text(prompt, p_path)
            art.prop_paths.append(p_path)

    return art

