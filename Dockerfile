# Use Python 3.11
FROM python:3.11-slim

# Install system dependencies for OCR, Audio, and Image processing
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    ffmpeg \
    libsm6 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Create necessary directories
RUN mkdir -p static

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Expose the single unified port
EXPOSE 8000

# Start everything
CMD ["python", "run_system.py"]
