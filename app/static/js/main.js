document.addEventListener('DOMContentLoaded', function() {
    // DOM Elements
    const dropArea = document.getElementById('drop-area');
    const fileInput = document.getElementById('file-input');
    const uploadForm = document.getElementById('upload-form');
    const fileDetails = document.getElementById('file-details');
    const filenameDisplay = document.getElementById('filename-display');
    const pageCountDisplay = document.getElementById('page-count-display');
    const generateBtn = document.getElementById('generate-btn');
    const progressContainer = document.getElementById('progress-container');
    const progressFill = document.getElementById('progress-fill');
    const statusMessage = document.getElementById('status-message');
    const viewerSection = document.getElementById('viewer-section');
    const prevBtn = document.getElementById('prev-btn');
    const nextBtn = document.getElementById('next-btn');
    const currentPageSpan = document.getElementById('current-page');
    const totalPagesSpan = document.getElementById('total-pages');
    const pageDisplay = document.getElementById('page-display');
    const errorModal = document.getElementById('error-modal');
    const errorMessage = document.getElementById('error-message');
    const closeBtn = document.querySelector('.close-btn');

    // State
    let currentState = {
        uploadedFile: null,
        originalPageCount: 0,
        processedFilename: null,
        totalPages: 0,
        currentPage: 1
    };

    // Event Listeners for Drag and Drop
    ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, preventDefaults, false);
    });

    function preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    ['dragenter', 'dragover'].forEach(eventName => {
        dropArea.addEventListener(eventName, highlight, false);
    });

    ['dragleave', 'drop'].forEach(eventName => {
        dropArea.addEventListener(eventName, unhighlight, false);
    });

    function highlight() {
        dropArea.classList.add('drag-over');
    }

    function unhighlight() {
        dropArea.classList.remove('drag-over');
    }

    // Handle file drop
    dropArea.addEventListener('drop', handleDrop, false);

    function handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;
        
        if (files.length > 0) {
            handleFiles(files);
        }
    }

    // Handle file selection
    fileInput.addEventListener('change', function() {
        if (fileInput.files.length > 0) {
            handleFiles(fileInput.files);
        }
    });

    // Click on drop area to open file dialog
    dropArea.addEventListener('click', function() {
        fileInput.click();
    });

    // Handle files
    function handleFiles(files) {
        const file = files[0];
        
        // Check if file is a PDF
        if (file.type !== 'application/pdf') {
            showError('Please upload a PDF file.');
            return;
        }
        
        uploadFile(file);
    }

    // Upload file to server
    function uploadFile(file) {
        const formData = new FormData();
        formData.append('file', file);
        
        // Show loading state
        statusMessage.textContent = 'Uploading file...';
        progressContainer.classList.remove('hidden');
        progressFill.style.width = '20%';
        
        fetch('/upload', {
            method: 'POST',
            body: formData
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Something went wrong during upload');
                });
            }
            return response.json();
        })
        .then(data => {
            // Update state
            currentState.uploadedFile = data.filename;
            currentState.originalPageCount = data.original_pages;
            
            // Show file details
            filenameDisplay.textContent = `File: ${file.name}`;
            pageCountDisplay.textContent = `Pages: ${data.original_pages}`;
            fileDetails.classList.remove('hidden');
            progressContainer.classList.add('hidden');
        })
        .catch(error => {
            showError(error.message);
            progressContainer.classList.add('hidden');
        });
    }

    // Generate AI notes
    generateBtn.addEventListener('click', function() {
        if (!currentState.uploadedFile) {
            showError('Please upload a PDF file first.');
            return;
        }
        
        // Show loading state
        statusMessage.textContent = 'Generating AI notes...';
        progressContainer.classList.remove('hidden');
        fileDetails.classList.add('hidden');
        progressFill.style.width = '40%';
        
        fetch('/generate-notes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                filename: currentState.uploadedFile
            })
        })
        .then(response => {
            if (!response.ok) {
                return response.json().then(data => {
                    throw new Error(data.error || 'Something went wrong during note generation');
                });
            }
            progressFill.style.width = '80%';
            return response.json();
        })
        .then(data => {
            // Update state
            currentState.processedFilename = data.processed_file;
            currentState.totalPages = data.total_pages;
            currentState.currentPage = 1;
            
            // Update UI
            totalPagesSpan.textContent = data.total_pages;
            currentPageSpan.textContent = '1';
            
            // Show viewer section
            viewerSection.classList.remove('hidden');
            progressFill.style.width = '100%';
            
            // Load first page
            loadPage(1);
            
            // Hide progress after a short delay
            setTimeout(() => {
                progressContainer.classList.add('hidden');
            }, 500);
        })
        .catch(error => {
            showError(error.message);
            fileDetails.classList.remove('hidden');
            progressContainer.classList.add('hidden');
        });
    });

    // Navigation
    prevBtn.addEventListener('click', function() {
        if (currentState.currentPage > 1) {
            currentState.currentPage--;
            loadPage(currentState.currentPage);
        }
    });

    nextBtn.addEventListener('click', function() {
        if (currentState.currentPage < currentState.totalPages) {
            currentState.currentPage++;
            loadPage(currentState.currentPage);
        }
    });

    // Load page
    function loadPage(pageNum) {
        // Update UI
        currentPageSpan.textContent = pageNum;
        
        // Show loading state
        pageDisplay.src = '';
        pageDisplay.alt = 'Loading...';
        
        // Fetch page image
        const pageSrc = `/get-page/${currentState.processedFilename}/${pageNum - 1}`;
        
        // Create a new image to preload
        const img = new Image();
        img.onload = function() {
            pageDisplay.src = pageSrc;
            pageDisplay.alt = `Page ${pageNum}`;
        };
        img.onerror = function() {
            showError(`Failed to load page ${pageNum}`);
            pageDisplay.alt = 'Error loading page';
        };
        img.src = pageSrc;
        
        // Update button states
        prevBtn.disabled = pageNum <= 1;
        nextBtn.disabled = pageNum >= currentState.totalPages;
    }

    // Error handling
    function showError(message) {
        errorMessage.textContent = message;
        errorModal.classList.remove('hidden');
    }

    closeBtn.addEventListener('click', function() {
        errorModal.classList.add('hidden');
    });

    // Close modal when clicking outside
    window.addEventListener('click', function(e) {
        if (e.target === errorModal) {
            errorModal.classList.add('hidden');
        }
    });

    // Keyboard navigation
    document.addEventListener('keydown', function(e) {
        // Only handle keyboard if viewer is visible
        if (viewerSection.classList.contains('hidden')) {
            return;
        }
        
        if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
            prevBtn.click();
        } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
            nextBtn.click();
        }
    });
});