from dataclasses import dataclass

PAINTINGS = {
    "starry_night": "Vincent van Gogh's Starry Night",
    "mona_lisa": "Leonardo da Vinci's Mona Lisa",
    "the_scream": "Edvard Munch's The Scream",
}

DEFAULT_FAMILY_VALUE = "kindness"


@dataclass
class UserConfig:
    painting_id: str
    child_name: str
    child_age: int
    family_value: str


class ValidationError(Exception):
    """Raised when user configuration is invalid."""


def normalize_user_config(cfg: UserConfig) -> UserConfig:
    cfg.child_name = cfg.child_name.strip().title()
    cfg.family_value = (cfg.family_value or DEFAULT_FAMILY_VALUE).strip().lower()
    cfg.painting_id = cfg.painting_id.strip().lower()
    return cfg


def validate_user_config(cfg: UserConfig) -> None:
    if cfg.painting_id not in PAINTINGS:
        raise ValidationError(
            f"Unknown painting_id: {cfg.painting_id}. "
            f"Must be one of {list(PAINTINGS.keys())}"
        )
    if not (1 <= cfg.child_age <= 12):
        raise ValidationError("child_age must be between 1 and 12")
    if not cfg.child_name:
        raise ValidationError("child_name is required")
    if not cfg.family_value:
        raise ValidationError("family_value is required")


def describe_painting(cfg: UserConfig) -> str:
    """Return the human-friendly description of the chosen painting."""
    return PAINTINGS.get(cfg.painting_id, cfg.painting_id)
