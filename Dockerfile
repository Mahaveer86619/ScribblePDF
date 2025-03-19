FROM python:slim

# Set working directory
WORKDIR /app

# Install system dependencies required for PDF processing
RUN apt-get update && apt-get install -y \
    poppler-utils \
    ghostscript \
    libgl1-mesa-glx \
    libglib2.0-0 \
    fonts-freefont-ttf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code
COPY . .

# Create directories needed by the application
RUN mkdir -p /app/app/static/uploads /app/app/static/processed /app/app/static/fonts

# Download a handwriting font
RUN mkdir -p /tmp/fonts && \
    cd /tmp/fonts && \
    pip install gdown && \
    gdown --fuzzy https://drive.google.com/file/d/1nxLWHPrq3r5Xj0UbD2eyZ7nOHt8OJRvE/view?usp=sharing && \
    mkdir -p /app/app/static/fonts && \
    mv /tmp/fonts/handwriting.ttf /app/app/static/fonts/ || echo "Font download failed, will use default"

# Set environment variables
ENV PYTHONPATH=/app
ENV FLASK_APP=run.py
ENV FLASK_ENV=production
ENV PYTHONUNBUFFERED=1

# Expose port
EXPOSE 5000

# Run the application
CMD ["python", "run.py"]