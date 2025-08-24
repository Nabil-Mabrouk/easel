from pydantic import BaseModel
from typing import List, Optional


class Character(BaseModel):
    name: str
    role: str  # hero, sidekick, mentor, etc.
    description: str
    visual_traits: str
    image_path: Optional[str] = None


class Illustration(BaseModel):
    prompt: str
    image_path: Optional[str] = None


class Page(BaseModel):
    number: int
    text: str
    art_direction: str
    illustration: Optional[Illustration] = None


class Storybook(BaseModel):
    title: str
    painting: dict
    characters: List[Character]
    pages: List[Page]
    closing_note: Optional[str] = None


class Storybook(BaseModel):
    title: str
    painting: dict
    characters: List[Character]  # NEW → character sheet
    pages: List[Page]
    closing_note: Optional[str] = None
