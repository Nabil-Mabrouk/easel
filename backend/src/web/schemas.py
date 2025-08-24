from pydantic import BaseModel, Field

class GenerateRequest(BaseModel):
    painting_id: str = Field(..., examples=["starry_night"])
    child_name: str = Field(..., examples=["Emma"])
    child_age: int = Field(..., ge=1, le=12, examples=[6])
    family_value: str = Field(..., examples=["sharing"])
    fallback: bool = False

class GenerateResponse(BaseModel):
    download_url: str
