from flask import Blueprint, render_template, request, jsonify, current_app, url_for, send_from_directory
import os
import uuid
import traceback
from werkzeug.utils import secure_filename
from app.utils.pdf_processor import process_pdf, is_pdf_file
from app.utils.gemini_client import generate_notes

main = Blueprint('main', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf'}

@main.route('/')
def index():
    """Render the main page"""
    return render_template('index.html')

@main.route('/upload', methods=['POST'])
def upload_file():
    """Handle PDF file upload and processing"""
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    
    if file.filename == '':
        return jsonify({'error': 'No file selected'}), 400
    
    if not file or not is_pdf_file(file.filename):
        return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400
    
    try:
        # Create unique filename
        unique_filename = f"{uuid.uuid4().hex}_{secure_filename(file.filename)}"
        filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(filepath)
        
        # Extract original page count before processing
        pages_info = process_pdf(filepath, get_info_only=True)
        
        return jsonify({
            'status': 'success',
            'filename': unique_filename,
            'original_pages': pages_info['page_count'],
            'message': 'File uploaded successfully'
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@main.route('/generate-notes', methods=['POST'])
def generate_ai_notes():
    """Generate AI handwritten notes for the uploaded PDF"""
    data = request.json
    filename = data.get('filename')
    
    if not filename:
        return jsonify({'error': 'No filename provided'}), 400
    
    filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    
    if not os.path.exists(filepath):
        return jsonify({'error': 'File not found'}), 404
    
    try:
        # Process the PDF and generate notes
        result = process_pdf(filepath)
        
        processed_filepath = os.path.join(
            current_app.config['PROCESSED_FOLDER'], 
            f"processed_{filename}"
        )
        
        # Generate notes for each extracted content
        for i, page_content in enumerate(result['extracted_contents']):
            # Only generate notes for original pages (not blank pages)
            if i % 2 == 0:  # Original pages are at even indices
                note_image = generate_notes(page_content)
                
                # Save the note image to be inserted after the original page
                result['note_images'][i//2] = note_image
        
        # Create the final PDF with original pages and inserted note pages
        final_pdf_path = result['create_annotated_pdf'](processed_filepath)
        
        return jsonify({
            'status': 'success',
            'processed_file': os.path.basename(final_pdf_path),
            'total_pages': result['total_pages'] * 2,  # Original + note pages
            'message': 'Notes generated successfully'
        })
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@main.route('/get-page/<filename>/<int:page_num>', methods=['GET'])
def get_page(filename, page_num):
    """Get a specific page image from the processed PDF"""
    try:
        processed_filepath = os.path.join(current_app.config['PROCESSED_FOLDER'], filename)
        
        if not os.path.exists(processed_filepath):
            return jsonify({'error': 'Processed file not found'}), 404
        
        # Extract the requested page as an image
        page_image_path = os.path.join(
            current_app.config['PROCESSED_FOLDER'],
            f"{os.path.splitext(filename)[0]}_page_{page_num}.png"
        )
        
        # If page image doesn't exist yet, extract it
        if not os.path.exists(page_image_path):
            from app.utils.pdf_processor import extract_page_as_image
            extract_page_as_image(processed_filepath, page_num, page_image_path)
        
        # Return the image
        return send_from_directory(
            current_app.config['PROCESSED_FOLDER'],
            f"{os.path.splitext(filename)[0]}_page_{page_num}.png"
        )
    
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500