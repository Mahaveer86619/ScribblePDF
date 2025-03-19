# app/pdf_processing.py
import io
from PyPDF2 import PdfReader
from PIL import Image, ImageDraw, ImageFont
from app.gemini_client import generate_ai_notes

def extract_pdf_content(pdf_path: str):
    """
    Extract text content from each page of the PDF.
    Note: Image extraction is not trivial with PyPDF2 so it's simulated as empty.
    Returns a list of dictionaries with keys 'text' and 'images'.
    """
    pages = []
    try:
        reader = PdfReader(pdf_path)
        for page in reader.pages:
            text = page.extract_text() or ""
            # For this example, we simulate no image extraction.
            images = []
            pages.append({"text": text, "images": images})
    except Exception as e:
        raise Exception(f"Failed to extract PDF content: {str(e)}")
    return pages

def generate_annotated_pages(pdf_path: str):
    """
    Process the PDF to generate annotated pages.
    For each page, an image is generated from its text and an additional blank page with AI-generated notes is inserted.
    Returns a list of PIL Image objects.
    """
    pages_content = extract_pdf_content(pdf_path)
    annotated_pages = []
    for content in pages_content:
        # Create an image simulating the original PDF page using its text.
        orig_img = Image.new("RGB", (600, 800), color="white")
        draw = ImageDraw.Draw(orig_img)
        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except Exception:
            font = ImageFont.load_default()
        # Draw the extracted text onto the image (wrap text if needed)
        draw.multiline_text((10, 10), content["text"], fill="black", font=font)
        annotated_pages.append(orig_img)

        # Generate the AI handwritten notes page using the Gemini API integration.
        try:
            ai_notes_img = generate_ai_notes(content["text"], content["images"])
            annotated_pages.append(ai_notes_img)
        except Exception as e:
            # If AI note generation fails, create a blank page with an error message.
            error_page = Image.new("RGB", (600, 800), color="white")
            error_draw = ImageDraw.Draw(error_page)
            error_draw.multiline_text((50, 50), f"Error generating AI notes:\n{str(e)}", fill="red", font=font)
            annotated_pages.append(error_page)
    return annotated_pages
