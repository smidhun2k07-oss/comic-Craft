from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from models.exporters import save_pdf
from models.gemini_flash import generate_outline
from models.gemini_pro import generate_story
from models.image_generator import generate_image
from models.layout_builder import build_comic_layout

BASE_DIR = Path(__file__).resolve().parent
router = APIRouter()
templates = Jinja2Templates(directory=str(BASE_DIR / "models" / "templates"))


@router.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@router.post("/generate", response_class=HTMLResponse)
async def generate_comic(
    request: Request,
    story_prompt: str = Form(...),
    character_name: str = Form("Alex"),
    setting: str = Form("forest"),
    tone: str = Form("adventurous"),
    art_style: str = Form("anime"),
):
    try:
        if not story_prompt or not story_prompt.strip():
            raise ValueError("Story prompt is required.")

        outline = generate_outline(story_prompt, character_name, setting, tone, art_style)
        if not isinstance(outline, list) or not outline:
            raise ValueError("The AI could not generate a usable comic outline.")

        story_text = generate_story(outline, character_name, setting, tone) or ""

        image_paths = []
        for idx, panel in enumerate(outline, start=1):
            image_prompt = panel.get("image_prompt") or panel.get("scene_description") or story_prompt
            image_paths.append(generate_image(image_prompt, idx, art_style))

        layout = build_comic_layout(outline, story_text, image_paths)
        if not layout:
            raise ValueError("The AI could not generate a valid comic layout.")

        pdf_url, _ = save_pdf(layout, character_name)

        return templates.TemplateResponse(
            "comic_preview.html",
            {
                "request": request,
                "layout": layout,
                "character_name": character_name,
                "pdf_url": pdf_url,
            },
        )
    except Exception as exc:
        print(f"Generate route error: {exc}")
        return templates.TemplateResponse(
            "index.html",
            {
                "request": request,
                "error": "Comic generation failed. Please try a different prompt or check your Gemini/API setup.",
            },
            status_code=400,
        )


@router.get("/export-success", response_class=HTMLResponse)
async def export_success(request: Request):
    return templates.TemplateResponse("export_success.html", {"request": request})
