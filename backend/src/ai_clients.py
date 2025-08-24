import os
import json
import base64
import argparse
import requests
from pathlib import Path
from typing import Optional, Dict, Any, Type, TypeVar

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel
from PIL import Image

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

# --- Availability Flags ---
RICH_AVAILABLE = True
PYDANTIC_AVAILABLE = True
PIL_AVAILABLE = True

# --- Environment Setup ---
load_dotenv()
API_KEY = os.getenv("AIMLAPI_KEY")

# --- Model Configurations ---
TEXT_MODEL = os.getenv("AIML_TEXT_MODEL", "openai/gpt-5-mini-2025-08-07")
IMAGE_MODEL = os.getenv("AIML_IMAGE_MODEL", "openai/gpt-image-1")
I2I_MODEL = os.getenv("AIML_I2I_MODEL", "bytedance/seededit-3.0-i2i")
EDIT_MODEL = os.getenv("AIML_EDIT_MODEL", "openai/gpt-image-1")
MULTIMODAL_MODEL = os.getenv("AIML_MULTIMODAL_MODEL", "openai/gpt-5-2025-08-07")

# --- Client Initialization ---
client = None
console = Console()
if API_KEY:
    client = OpenAI(base_url="https://api.aimlapi.com/v1", api_key=API_KEY)
else:
    console.print("[yellow]Warning: AIMLAPI_KEY not found. AI functions will be disabled.[/yellow]")

# --- Typing ---
PydanticModel = TypeVar("PydanticModel", bound=BaseModel)

# =============================================================================
# Core Functions
# =============================================================================

def generate_text(system_prompt: str, user_prompt: str) -> Optional[str]:
    """Generate plain text content from the text model."""
    if not client:
        Console().print("[red]❌ No client available. Did you set AIMLAPI_KEY?[/red]")
        return None
    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            seed=42,
            temperature=1.0,
            max_tokens=2000,
        )

        content = response.choices[0].message.content
        if not content:
            Console().print("[red]❌ Empty content returned by API[/red]")
            Console().print(response)
            return None

        return content.strip()

    except Exception as e:
        import traceback
        Console().print("[red]❌ Exception in generate_text[/red]")
        Console().print(f"[yellow]{str(e)}[/yellow]")
        Console().print(traceback.format_exc())
        return None



def generate_json(system_prompt: str, user_prompt: str) -> Optional[Dict[str, Any]]:
    """Generate structured text content as JSON using the text model."""
    if not client:
        return None
    try:
        response = client.chat.completions.create(
            model=TEXT_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            seed=42,
            temperature=1,
            max_tokens=2000,
            response_format={"type": "json_object"},
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        console.print(f"[red]Error in generate_json: {e}[/red]")
        return None


def generate_image_from_text(prompt: str, output_path: Path) -> Optional[Path]:
    """Generate an image from a text prompt and save to file."""
    if not API_KEY:
        return None
    try:
        api_response = requests.post(
            "https://api.aimlapi.com/v1/images/generations",
            headers={"Authorization": f"Bearer {API_KEY}"},
            json={"prompt": prompt, "model": IMAGE_MODEL},
            timeout=90,
        )
        api_response.raise_for_status()
        data = api_response.json()

        image_url = _extract_image_url_from_response(data)
        if not image_url:
            console.print(f"[red]No image URL in API response. Response: {data}[/red]")
            return None

        image_response = requests.get(image_url, timeout=60)
        image_response.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(image_response.content)
        return output_path
    except requests.exceptions.RequestException as e:
        console.print(f"[red]Image generation error: {e}[/red]")
        return None


# def generate_image_from_image(prompt: str, base_image_path: Path, output_path: Path) -> Optional[Path]:
#     """Modify an existing image using a text prompt (Image-to-Image)."""
#     if not client:
#         return None
#     try:
#         with open(base_image_path, "rb") as image_file:
#             response = client.images.edit(
#                 model=EDIT_MODEL,
#                 image=image_file,
#                 prompt=prompt,
#             )

#         modified_image_url = response.data[0].url
#         if not modified_image_url:
#             console.print("[red]I2I Error: No URL in Edit API response.[/red]")
#             return None

#         image_response = requests.get(modified_image_url, timeout=60)
#         image_response.raise_for_status()
#         output_path.parent.mkdir(parents=True, exist_ok=True)
#         with open(output_path, "wb") as f:
#             f.write(image_response.content)
#         return output_path
#     except Exception as e:
#         console.print(f"[red]Error in generate_image_from_image: {e}[/red]")
#         return None


def generate_structured_text(system_prompt: str, user_prompt: str, pydantic_model: Type[PydanticModel]) -> Optional[PydanticModel]:
    """Generate structured JSON output validated against a Pydantic model."""
    if not client or not PYDANTIC_AVAILABLE:
        return None
    try:
        response = client.chat.completions.create(
            model=MULTIMODAL_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            response_format={
                "type": "json_schema",
                "json_schema": {
                    "name": pydantic_model.__name__,
                    "schema": pydantic_model.model_json_schema(),
                },
            },
            temperature=0.7,
            max_tokens=4000,
        )
        content = response.choices[0].message.content

        if hasattr(pydantic_model, "model_validate_json"):  # Pydantic v2
            return pydantic_model.model_validate_json(content)
        return pydantic_model.parse_raw(content)  # Pydantic v1 fallback
    except Exception as e:
        console.print(f"[red]Error in generate_structured_text: {e}[/red]")
        return None


def generate_response_from_image_and_text(prompt: str, image_path: Path) -> Optional[str]:
    """Generate a text response from a prompt and an input image (multimodal)."""
    if not client:
        return None

    image_uri = _get_image_data_uri(image_path)
    if not image_uri:
        return None

    try:
        response = client.chat.completions.create(
            model=MULTIMODAL_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_uri}},
                ],
            }],
            max_tokens=1024,
        )
        return response.choices[0].message.content
    except Exception as e:
        console.print(f"[red]Error in generate_response_from_image_and_text: {e}[/red]")
        return None

def generate_image_from_images(prompt: str, image_paths: list[Path], output_path: Path) -> Optional[Path]:
    """Modify one or multiple images using a text prompt by manually building a multipart request."""
    if not API_KEY:
        return None

    files_to_upload = []
    
    try:
        # Prepare the multipart/form-data payload
        # The API expects the prompt and model as form fields, and images as file parts.
        data = {"prompt": prompt, "model": EDIT_MODEL}
        
        # Flatten list and prepare files for upload
        flat_paths = [p for sublist in image_paths if isinstance(sublist, list) for p in sublist] + \
                     [p for p in image_paths if not isinstance(p, list)]

        for i, path in enumerate(flat_paths):
            if path.exists():
                # Each file is a tuple: (form_field_name, (filename, file_object, content_type))
                files_to_upload.append(
                    ('image', (path.name, open(path, 'rb'), 'image/png'))
                )
            else:
                console.print(f"[yellow]Warning: Reference image not found, skipping: {path}[/yellow]")
        
        if not files_to_upload:
            raise ValueError("No valid image files were provided for editing.")

        # Make the request to the edits endpoint
        api_response = requests.post(
            "https://api.aimlapi.com/v1/images/edits",
            headers={"Authorization": f"Bearer {API_KEY}"},
            data=data,
            files=files_to_upload,
            timeout=120,
        )
        api_response.raise_for_status()
        response_data = api_response.json()

        modified_image_url = _extract_image_url_from_response(response_data)
        if not modified_image_url:
            console.print(f"[red]I2I Error: No URL in Edit API response. Response: {response_data}[/red]")
            return None

        image_response = requests.get(modified_image_url, timeout=60)
        image_response.raise_for_status()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(image_response.content)

        return output_path

    except Exception as e:
        console.print(f"[red]Error in generate_image_from_images: {e}[/red]")
        # Create a fallback placeholder image on error
        Image.new("RGB", (1024, 1024), (240, 240, 240)).save(output_path)
        return output_path

    finally:
        # Ensure all opened file objects are closed
        for _, (_, file_obj, _) in files_to_upload:
            try:
                file_obj.close()
            except Exception:
                pass


def generate_image_from_image(prompt: str, base_image_path: Path, output_path: Path) -> Optional[Path]:
    """Wrapper: single image edit using generate_image_from_images."""
    return generate_image_from_images(prompt, [base_image_path], output_path)

# =============================================================================
# Helper Functions
# =============================================================================

def _extract_image_url_from_response(data: Dict[str, Any]) -> Optional[str]:
    """Extract image URL from API response supporting both 'images' and 'data' keys."""
    image_list = data.get("images") or data.get("data")
    if image_list and isinstance(image_list, list) and len(image_list) > 0:
        return image_list[0].get("url")
    return None


def _get_image_data_uri(image_path: Path) -> Optional[str]:
    """Convert a local image file to a base64 data URI."""
    try:
        mime_map = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".webp": "image/webp"}
        mime_type = mime_map.get(image_path.suffix.lower())
        if not mime_type:
            raise ValueError(f"Unsupported image format: {image_path.suffix}")

        with open(image_path, "rb") as img_file:
            encoded = base64.b64encode(img_file.read()).decode("utf-8")
        return f"data:{mime_type};base64,{encoded}"
    except Exception as e:
        console.print(f"[red]Error encoding image: {e}[/red]")
        return None

def load_fallback_json(path: Path) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# =============================================================================
# Test Suite Entrypoint
# =============================================================================

def _test_text():
    result = generate_text("You are a helpful writer.", "Say 'Hello from AIML API' in one sentence.")
    ok = result and "hello" in result.lower()
    return ("Text", ok, result)

def _test_tti():
    out = Path("fallback/tti_test.png")
    out.parent.mkdir(exist_ok=True)
    path = generate_image_from_text("A cheerful cartoon star with a smile", out)
    return ("Text-to-Image", path is not None, str(path) if path else None)

def _test_structured():
    from pydantic import BaseModel

    class Demo(BaseModel):
        greeting: str
        lang: str

    data = generate_structured_text(
        "Return JSON only",
        "greeting='hello', lang='en'",
        Demo
    )
    return ("Structured", data is not None, data.model_dump() if data else None)


def _test_multi_i2i():
    """Test multi-image + prompt editing pipeline."""
    out = Path("fallback/multi_i2i_test.png")
    out.parent.mkdir(exist_ok=True)

    # We'll try with some small placeholder refs (you should replace with real files)
    refs = [Path("fallback/tti_test.png")]  # add more refs if available
    path = generate_image_from_images(
        "Make the star wear sunglasses and smile wider",
        refs,
        out
    )
    return ("Multi-Image Edit", path is not None, str(path) if path else None)


def _render_summary(rows):
    table = Table(title="AI Client Test Summary")
    table.add_column("Test", style="cyan")
    table.add_column("OK", style="green")
    table.add_column("Details", style="white")
    for name, ok, detail in rows:
        table.add_row(name, "✅" if ok else "❌", str(detail)[:120])
    console.print(Panel.fit(table))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Client for KidsBookAI — test utilities.")
    parser.add_argument("--test-text", action="store_true", help="Run the text generation test only.")
    parser.add_argument("--test-tti", action="store_true", help="Run the text-to-image test only.")
    parser.add_argument("--test-structured", action="store_true", help="Run the structured output test only.")
    parser.add_argument("--test-multi-i2i", action="store_true", help="Run the multi-image edit test only.")
    args = parser.parse_args()

    rows = []
    if args.test_text or args.test_tti or args.test_structured or args.test_multi_i2i:
        if args.test_text: rows.append(_test_text())
        if args.test_tti: rows.append(_test_tti())
        if args.test_structured: rows.append(_test_structured())
        if args.test_multi_i2i: rows.append(_test_multi_i2i())
    else:
        rows.append(_test_text())
        rows.append(_test_tti())
        rows.append(_test_structured())
        rows.append(_test_multi_i2i())

    _render_summary(rows)