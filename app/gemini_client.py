# app/gemini_client.py
import os
import requests
from PIL import Image, ImageDraw, ImageFont

def generate_ai_notes(text: str, images: list):
    """
    Call the Gemini API to generate AI handwritten notes.
    This function sends the page text (and images if available) to the Gemini API.
    In this example, we simulate the API call by generating an image with handwritten-style annotations.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("Gemini API key not set in environment variables.")

    # Simulate API payload
    payload = {
        "text": text,
        "images": images,
        "style": "handwritten",
        "annotations": {
            "arrows": True,
            "underlines": True,
            "pencil_texture": True
        }
    }
    headers = {"Authorization": f"Bearer {api_key}"}

    # Uncomment and adjust the following lines if you have an actual Gemini API endpoint.
    # try:
    #     response = requests.post("https://api.gemini.example.com/generate_notes", json=payload, headers=headers, timeout=30)
    #     response.raise_for_status()
    #     # Process the response to create an image (this depends on the API response structure)
    #     # For example, if the API returns an image URL or base64 image, load it accordingly.
    #     # For now, we assume the API returns binary image data:
    #     img_data = response.content
    #     ai_notes_img = Image.open(io.BytesIO(img_data))
    #     return ai_notes_img
    # except Exception as e:
    #     raise Exception(f"Gemini API call failed: {str(e)}")

    # For demonstration, we simulate the AI-generated handwritten notes image:
    ai_notes_img = Image.new("RGB", (600, 800), color="white")
    draw = ImageDraw.Draw(ai_notes_img)
    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except Exception:
        font = ImageFont.load_default()
    # Draw simulated handwritten text with spacing, arrow pointers and underlines
    simulated_text = "AI Generated Notes:\n" + text[:300]  # truncate text for layout
    draw.multiline_text((50, 50), simulated_text, fill="black", font=font, spacing=4)

    # Simulate pencil underlines (rough lines below some text segments)
    underline_y = 120
    draw.line((50, underline_y, 550, underline_y), fill="gray", width=2)

    # Simulate arrow pointer for topics
    arrow_start = (50, underline_y + 20)
    arrow_end = (80, underline_y + 20)
    draw.line((arrow_start, arrow_end), fill="black", width=3)
    draw.polygon([arrow_end, (arrow_end[0]-5, arrow_end[1]-5), (arrow_end[0]-5, arrow_end[1]+5)], fill="black")

    return ai_notes_img
