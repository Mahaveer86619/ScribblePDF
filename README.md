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

1.  Clone the repository:
    ```bash
    git clone <repository_url>
    cd ScribblePDF
    ```
2.  Build the Docker image:
    ```bash
    docker build -t scribblepdf .
    ```
3.  Run the Docker container:
    ```bash
    docker run -p 5000:5000 scribblepdf
    ```
4.  Open your web browser and navigate to `http://localhost:5000`.

### Usage

1.  Upload a PDF file.
2.  Click the "Generate AI Notes" button.
3.  View the annotated PDF.

## Future Enhancements

* Multiple note-taking themes (pen, marker, etc.).
* Customizable note styles and layouts.
* Enhanced AI model for improved note generation.
* User account.
* Save the modified pdf.

## Contributing

Contributions are welcome! Please submit a pull request or create an issue.