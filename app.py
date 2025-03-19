from flask import Flask, render_template, request, send_from_directory, jsonify
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfFileReader, PdfFileWriter
from PIL import Image
import io
import requests
import base64

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['GENERATED_FOLDER'] = 'generated'

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['GENERATED_FOLDER'], exist_ok=True)

# Replace with your Hugging Face Gemini model API endpoint
HUGGING_FACE_API_URL = 'https://api-inference.huggingface.co/models/YOUR_GEMINI_MODEL'
HUGGING_FACE_API_KEY = 'YOUR_HUGGING_FACE_API_KEY'

def extract_text_and_images(pdf_path):
    pdf_reader = PdfFileReader(pdf_path)
    contents = []
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        text = page.extractText()
        contents.append({"text": text, "images": []})  # Add image extraction logic if needed
    return contents

def generate_ai_notes(content):
    headers = {"Authorization": f"Bearer {HUGGING_FACE_API_KEY}"}
    response = requests.post(HUGGING_FACE_API_URL, headers=headers, json={"inputs": content})
    return response.json()

def create_handwritten_style_image(content):
    # Placeholder function to create handwritten style image
    # Replace with actual implementation using PIL and AI-generated notes
    img = Image.new('RGB', (595, 842), color='white')  # A4 size
    return img

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No file part"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
    if file:
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        return jsonify({"filename": filename}), 200

@app.route('/generate_notes', methods=['POST'])
def generate_notes():
    filename = request.json.get('filename')
    if not filename:
        return jsonify({"error": "Filename not provided"}), 400

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    contents = extract_text_and_images(file_path)

    generated_notes = []
    for content in contents:
        ai_note = generate_ai_notes(content['text'])
        handwritten_image = create_handwritten_style_image(ai_note)
        img_byte_arr = io.BytesIO()
        handwritten_image.save(img_byte_arr, format='PNG')
        img_byte_arr = img_byte_arr.getvalue()
        encoded_img = base64.b64encode(img_byte_arr).decode('utf-8')
        generated_notes.append(encoded_img)

    return jsonify({"notes": generated_notes}), 200

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

if __name__ == '__main__':
    app.run(debug=True)