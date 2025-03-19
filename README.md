# ScribblePDF - AI-Enhanced PDF Note Generation

ScribblePDF transforms static PDFs into interactive, handwritten note-style documents using AI.

## Features

* AI-generated handwritten notes with pencil texture.
* Arrow pointers and rough pencil underlines for highlighting.
* Dynamic page replacement for seamless viewing.
* Simple and engaging user interface.
* Adding blank pages in between original pdf pages for notes.
* Server-side rendering.

## Getting Started

### Prerequisites

* Docker
* Python 3.x

### Installation

1. Clone the repository:
```bash
git clone <repository_url>
cd ScribblePDF
```

2. Configure environment variables:
```bash
cp .env.example .env
```
Edit the `.env` file and add your Gemini API key.

3. Build and run with Docker Compose:
```bash
docker-compose up -d
```

4. Open your web browser and navigate to `http://localhost:5000`.

### Manual Installation (without Docker)

1. Clone the repository and navigate to the project directory.
2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Configure environment variables:
```bash
cp .env.example .env
```
5. Run the application:
```bash
python run.py
```

### Usage

1. Upload a PDF file.
2. Click the "Generate AI Notes" button.
3. View the annotated PDF with AI-generated handwritten notes.
4. Navigate through pages using the Previous/Next buttons or arrow keys.

## Technical Overview

### Components

* **Flask Backend**: Handles file uploads, PDF processing, and API endpoints.
* **Gemini API Integration**: Generates AI handwritten notes from PDF content.
* **PDF Processing**: Uses PyPDF2 and pdf2image for content extraction and page manipulation.
* **Interactive UI**: Responsive web interface for PDF viewing with handwritten notes.

### File Structure

```
ScribblePDF/
├── app/
│   ├── __init__.py         # Flask application initialization
│   ├── routes.py           # API routes and endpoints
│   ├── utils/
│   │   ├── pdf_processor.py    # PDF handling utilities
│   │   └── gemini_client.py    # Gemini API integration
│   ├── static/             # Static assets
│   └── templates/          # HTML templates
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose setup
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point
```

## Future Enhancements

* Multiple note-taking themes (pen, marker, etc.).
* Customizable note styles and layouts.
* Enhanced AI model for improved note generation.
* User account.
* Save the modified pdf.

## Contributing

Contributions are welcome! Please submit a pull request or create an issue.

## License

This project is licensed under the MIT License.