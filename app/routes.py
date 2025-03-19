# app/routes.py
import os
import shutil
import uuid
from fastapi import APIRouter, Request, UploadFile, File, Form, HTTPException
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from app.pdf_processing import extract_pdf_content, generate_annotated_pages
from pathlib import Path

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Ensure directories exist for uploads and generated images
UPLOAD_DIR = Path("app/uploads")
GENERATED_DIR = Path("app/static/generated")
UPLOAD_DIR.mkdir(exist_ok=True, parents=True)
GENERATED_DIR.mkdir(exist_ok=True, parents=True)

@router.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """
    Render the main page with upload form or generated pages.
    """
    # Check if there is a list of pages in session (or use query params)
    return templates.TemplateResponse("index.html", {"request": request, "pages": None, "error": None})

@router.post("/upload", response_class=HTMLResponse)
async def upload_pdf(request: Request, file: UploadFile = File(...)):
    """
    Handle PDF file upload, processing, and page generation.
    """
    if file.content_type != "application/pdf":
        return templates.TemplateResponse("index.html", {"request": request, "pages": None, "error": "Only PDF files are accepted."})

    # Save the uploaded file temporarily
    file_id = uuid.uuid4().hex
    temp_file_path = UPLOAD_DIR / f"{file_id}.pdf"
    try:
        with open(temp_file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "pages": None, "error": f"Error saving file: {str(e)}"})

    # Process the PDF: extract content and generate annotated pages (original + AI notes pages)
    try:
        annotated_images = generate_annotated_pages(str(temp_file_path))
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "pages": None, "error": f"Error processing PDF: {str(e)}"})

    # Save annotated pages to GENERATED_DIR and create URLs for display
    page_urls = []
    try:
        for idx, img in enumerate(annotated_images):
            image_filename = f"{file_id}_page_{idx}.png"
            image_path = GENERATED_DIR / image_filename
            img.save(image_path, format="PNG")
            page_urls.append(f"/static/generated/{image_filename}")
    except Exception as e:
        return templates.TemplateResponse("index.html", {"request": request, "pages": None, "error": f"Error saving generated images: {str(e)}"})

    # Optionally, clean up the uploaded PDF file
    try:
        os.remove(temp_file_path)
    except Exception:
        pass

    # Render the page viewer with the generated page URLs
    return templates.TemplateResponse("index.html", {"request": request, "pages": page_urls, "error": None})
