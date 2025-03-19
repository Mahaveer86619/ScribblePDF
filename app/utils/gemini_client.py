import os
import io
import base64
import requests
import json
from PIL import Image, ImageDraw, ImageFont
import numpy as np
import tempfile

# Check if the API key is set
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY environment variable is not set")

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-pro-vision:generateContent"

# Load handwriting-like fonts
try:
    # Try to load a handwriting font
    font_path = os.path.join(os.path.dirname(__file__), '../../app/static/fonts/handwriting.ttf')
    if not os.path.exists(font_path):
        # If the font doesn't exist, we'll use a default font later
        font_path = None
except Exception:
    font_path = None

def generate_notes(page_content):
    """
    Generate handwritten-style notes using Gemini model
    
    Args:
        page_content (dict): Dictionary containing text and image from PDF page
    
    Returns:
        PIL.Image: Image with handwritten-style notes
    """
    try:
        # Extract text and image from page content
        text = page_content['text']
        image_bytes = page_content['image']
        width = page_content['width']
        height = page_content['height']
        
        # Create prompt for Gemini
        prompt = """
        Create handwritten notes from this PDF page content. Focus on:
        1. Key concepts and important points
        2. Use arrows to connect related ideas
        3. Underline important parts with rough pencil lines
        4. Make it look natural and handwritten
        5. Keep some white space, don't fill the entire page
        6. Notes should be as if they were drawn with a pencil
        7. If there's math content, show rough workings
        8. Use simple drawings or diagrams where appropriate
        
        Format your response as a structured list of notes with positions
        (x, y coordinates), content (text or drawing instructions), and style (normal text, underline, arrow, etc.).
        """
        
        # Prepare image for API request
        image_base64 = base64.b64encode(image_bytes).decode('utf-8')
        
        # Construct API request
        request_data = {
            "contents": [
                {
                    "parts": [
                        {"text": prompt},
                        {
                            "inline_data": {
                                "mime_type": "image/png",
                                "data": image_base64
                            }
                        }
                    ]
                }
            ]
        }
        
        # Make API request
        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_KEY}",
            headers={"Content-Type": "application/json"},
            data=json.dumps(request_data)
        )
        
        response_data = response.json()
        
        # Check if the API call was successful
        if response.status_code != 200:
            error_message = response_data.get('error', {}).get('message', 'Unknown error')
            raise Exception(f"Gemini API error: {error_message}")
        
        # Extract AI-generated notes from response
        generated_content = response_data.get('candidates', [])[0].get('content', {}).get('parts', [])[0].get('text', '')
        
        # Parse the generated content to extract note information
        notes = parse_generated_notes(generated_content)
        
        # Create a blank page with pencil texture
        note_image = create_pencil_texture_background(width, height)
        draw = ImageDraw.Draw(note_image)
        
        # Try to load a handwriting-like font, or use default
        try:
            if font_path:
                base_font = ImageFont.truetype(font_path, 28)
            else:
                base_font = ImageFont.load_default()
        except Exception:
            base_font = ImageFont.load_default()
        
        # Draw the generated notes onto the blank page
        draw_notes_on_image(draw, notes, base_font, width, height)
        
        return note_image
    
    except Exception as e:
        # In case of error, return a blank page with error message
        error_image = create_pencil_texture_background(width, height)
        draw = ImageDraw.Draw(error_image)
        
        try:
            font = ImageFont.load_default()
            draw.text((50, 50), f"Error generating notes: {str(e)}", fill=(100, 100, 100), font=font)
        except Exception:
            # Fallback if even drawing error message fails
            pass
        
        return error_image

def parse_generated_notes(content):
    """
    Parse the AI-generated notes content into a structured format
    
    Args:
        content (str): Text response from Gemini API
    
    Returns:
        list: List of note elements with positions and styles
    """
    # This is a simplified parser - in a real application, you might want a more robust parser
    notes = []
    
    # Very simple parsing for demonstration - extract key points
    for line in content.split('\n'):
        if line.strip():
            # Create a random position for the note
            notes.append({
                'type': 'text',
                'content': line,
                'position': None,  # We'll assign positions later
                'style': 'normal'
            })
    
    return notes

def create_pencil_texture_background(width, height):
    """
    Create a background with pencil texture
    
    Args:
        width (int): Width of the image
        height (int): Height of the image
    
    Returns:
        PIL.Image: Image with pencil texture background
    """
    # Create a white background
    background = Image.new('RGB', (width, height), color=(255, 255, 255))
    draw = ImageDraw.Draw(background)
    
    # Add subtle texture (very light gray noise)
    for _ in range(width * height // 100):  # Adjust density as needed
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        gray = np.random.randint(240, 252)
        draw.point((x, y), fill=(gray, gray, gray))
    
    return background

def draw_notes_on_image(draw, notes, base_font, width, height):
    """
    Draw the generated notes onto an image
    
    Args:
        draw (PIL.ImageDraw.ImageDraw): Drawing context
        notes (list): List of note elements
        base_font (PIL.ImageFont.ImageFont): Base font for text
        width (int): Width of the image
        height (int): Height of the image
    
    Returns:
        None
    """
    # Define margin
    margin = 50
    
    # Default values for hand-drawn appearance
    pencil_color = (80, 80, 80)  # Dark gray for pencil
    
    # Layout the notes with some randomness to appear handwritten
    current_y = margin + np.random.randint(0, 30)
    
    for note in notes:
        # Skip empty notes
        if not note.get('content', '').strip():
            continue
        
        # Add some randomness to the position to make it look more natural
        current_x = margin + np.random.randint(0, 40)
        
        # Slightly vary the font size and rotation for a more natural look
        font_size = np.random.randint(22, 32)
        try:
            if font_path:
                font = ImageFont.truetype(font_path, font_size)
            else:
                font = base_font
        except Exception:
            font = base_font
        
        # Calculate text size and check if it fits on current line
        text_width = draw.textlength(note['content'], font=font)
        if current_x + text_width > width - margin:
            # Move to next line
            current_y += font_size * 1.5
            current_x = margin + np.random.randint(0, 40)
        
        # Draw text with slight variation in color to mimic pencil
        text_color = (np.random.randint(50, 90), np.random.randint(50, 90), np.random.randint(50, 90))
        
        # Add slight angle variation to text
        rotation_angle = np.random.uniform(-1, 1)
        
        # Draw the text
        draw.text((current_x, current_y), note['content'], fill=text_color, font=font)
        
        # Randomly underline some text (about 30% chance)
        if np.random.random() < 0.3:
            # Draw rough underline (not perfectly straight)
            y_underline = current_y + font_size + np.random.randint(0, 5)
            
            # Draw underline as a series of short, slightly uneven lines
            x_start = current_x
            while x_start < current_x + text_width:
                segment_length = np.random.randint(5, 20)
                y_variation = np.random.randint(-2, 3)
                draw.line(
                    (x_start, y_underline + y_variation, 
                     min(x_start + segment_length, current_x + text_width), y_underline + y_variation),
                    fill=pencil_color,
                    width=1
                )
                x_start += segment_length
        
        # Randomly add arrows (about 15% chance)
        if np.random.random() < 0.15:
            # Calculate arrow start position
            arrow_x = current_x - 20 + np.random.randint(-10, 10)
            arrow_y = current_y + font_size/2 + np.random.randint(-10, 10)
            
            # Draw arrow (simplified)
            arrow_length = np.random.randint(15, 25)
            draw.line(
                (arrow_x - arrow_length, arrow_y, arrow_x, arrow_y),
                fill=pencil_color,
                width=1
            )
            # Arrow head
            draw.line(
                (arrow_x, arrow_y, arrow_x - 5, arrow_y - 5),
                fill=pencil_color,
                width=1
            )
            draw.line(
                (arrow_x, arrow_y, arrow_x - 5, arrow_y + 5),
                fill=pencil_color,
                width=1
            )
        
        # Move down for next item
        current_y += font_size * 1.5
        
        # If we're getting too far down the page, reset to a new column
        if current_y > height - margin:
            current_y = margin + np.random.randint(0, 30)
            margin += width // 2  # Move to right half of page