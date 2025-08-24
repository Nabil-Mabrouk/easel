from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from pathlib import Path
from .schemas import GenerateRequest, GenerateResponse
from .services import generate_book_service
import os

router = APIRouter()

@router.post("/generate", response_model=GenerateResponse)
async def generate(req: GenerateRequest):
    url = await generate_book_service(req)
    return GenerateResponse(download_url=url)

@router.get("/download/{filename}")
async def download(filename: str):
    path = Path(os.getenv("OUTPUT_DIR", "output")) / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)
