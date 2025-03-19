import os
import PyPDF2
from PIL import Image, ImageDraw
import io
import tempfile
from pdf2image import convert_from_path
import numpy as np

def is_pdf_file(filename):
    """Check if the file is a PDF based on extension"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'pdf'}

def process_pdf(pdf_path, get_info_only=False):
    """
    Process a PDF file to extract text, images, and create annotated version
    
    Args:
        pdf_path (str): Path to the PDF file
        get_info_only (bool): If True, only return page count info
    
    Returns:
        dict: Results containing extracted content and functions to generate final PDF
    """
    try:
        # Open PDF file
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            total_pages = len(pdf_reader)
            
            if get_info_only:
                return {'page_count': total_pages}
            
            extracted_contents = []
            
            # Convert PDF pages to images for better processing
            images = convert_from_path(pdf_path)
            
            # Extract content from each page
            for i in range(total_pages):
                page = pdf_reader.pages[i]
                text = page.extract_text() or ""
                
                # Convert PIL Image to bytes for AI processing
                img_byte_arr = io.BytesIO()
                images[i].save(img_byte_arr, format='PNG')
                img_bytes = img_byte_arr.getvalue()
                
                # Store extracted content (both text and image)
                extracted_contents.append({
                    'page_number': i + 1,
                    'text': text,
                    'image': img_bytes,
                    'width': images[i].width,
                    'height': images[i].height
                })
            
            # Prepare storage for generated note images
            note_images = [None] * total_pages
            
            # Function to create the final annotated PDF
            def create_annotated_pdf(output_path):
                # Create a new PDF with blank pages inserted between original pages
                pdf_writer = PyPDF2.PdfWriter()
                
                # Create a temporary directory for intermediate files
                with tempfile.TemporaryDirectory() as temp_dir:
                    page_files = []
                    
                    for i in range(total_pages):
                        # Add original page
                        with open(pdf_path, 'rb') as input_file:
                            reader = PyPDF2.PdfReader(input_file)
                            pdf_writer.add_page(reader.pages[i])
                        
                        # Add blank page with handwritten notes if available
                        if note_images[i] is not None:
                            # Convert note image to PDF page
                            note_page_path = os.path.join(temp_dir, f"note_page_{i}.pdf")
                            note_images[i].save(note_page_path, "PDF")
                            
                            # Add the note page to the output PDF
                            with open(note_page_path, 'rb') as note_file:
                                note_reader = PyPDF2.PdfReader(note_file)
                                pdf_writer.add_page(note_reader.pages[0])
                        else:
                            # Add a blank page if no notes were generated
                            pdf_writer.add_blank_page()
                    
                    # Write the final PDF
                    with open(output_path, 'wb') as output_file:
                        pdf_writer.write(output_file)
                
                return output_path
            
            return {
                'total_pages': total_pages,
                'extracted_contents': extracted_contents,
                'note_images': note_images,
                'create_annotated_pdf': create_annotated_pdf
            }
    
    except Exception as e:
        raise Exception(f"Error processing PDF: {str(e)}")

def extract_page_as_image(pdf_path, page_num, output_path):
    """
    Extract a specific page from a PDF as an image
    
    Args:
        pdf_path (str): Path to the PDF file
        page_num (int): Page number to extract (0-indexed)
        output_path (str): Path to save the output image
    
    Returns:
        str: Path to the saved image
    """
    try:
        # Convert the specific page to an image
        images = convert_from_path(pdf_path, first_page=page_num+1, last_page=page_num+1)
        
        if images and len(images) > 0:
            # Save the image
            images[0].save(output_path, 'PNG')
            return output_path
        else:
            raise Exception(f"Could not extract page {page_num} from PDF")
    
    except Exception as e:
        raise Exception(f"Error extracting page as image: {str(e)}")

def create_blank_page_with_pencil_texture(width, height):
    """
    Create a blank page with a subtle pencil texture background
    
    Args:
        width (int): Width of the page
        height (int): Height of the page
    
    Returns:
        PIL.Image: Blank page with pencil texture
    """
    # Create a blank white page
    blank_page = Image.new('RGB', (width, height), color='white')
    
    # Add subtle pencil texture
    draw = ImageDraw.Draw(blank_page)
    
    # Create texture by adding random light gray points
    for _ in range(width * height // 100):  # Adjust density as needed
        x = np.random.randint(0, width)
        y = np.random.randint(0, height)
        # Very light gray dots
        gray_value = np.random.randint(230, 250)
        draw.point((x, y), fill=(gray_value, gray_value, gray_value))
    
    return blank_page