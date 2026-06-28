# ------------------------------------------------------
# Clinical Intelligence Copilot Backend
# Production Dockerfile
# ------------------------------------------------------

FROM python:3.11.7-slim

# Prevent Python from writing .pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Ensure stdout/stderr are sent directly to logs
ENV PYTHONUNBUFFERED=1

# Hugging Face model cache location
ENV HF_HOME=/root/.cache/huggingface

# Working directory
WORKDIR /app

# Install required Linux packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libpq-dev \
    mupdf \
    mupdf-tools \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency lock file first for better Docker layer caching
COPY requirements.lock .

# Upgrade pip
RUN pip install --upgrade pip

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.lock

# Pre-download embedding model so first request is fast
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy application source
COPY . .

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]