document.getElementById('upload-form').addEventListener('submit', function(event) {
    event.preventDefault();
    const fileInput = document.getElementById('file-input');
    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.filename) {
            document.getElementById('generate-notes-btn').disabled = false;
            document.getElementById('generate-notes-btn').setAttribute('data-filename', data.filename);
        }
    })
    .catch(error => console.error('Error:', error));
});

document.getElementById('generate-notes-btn').addEventListener('click', function() {
    const filename = this.getAttribute('data-filename');
    fetch('/generate_notes', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ filename: filename })
    })
    .then(response => response.json())
    .then(data => {
        const pdfDisplay = document.getElementById('pdf-display');
        pdfDisplay.innerHTML = '';
        data.notes.forEach(note => {
            const img = document.createElement('img');
            img.src = `data:image/png;base64,${note}`;
            pdfDisplay.appendChild(img);
        });
    })
    .catch(error => console.error('Error:', error));
});