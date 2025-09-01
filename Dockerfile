# Trading System - Backend Dockerfile
FROM python:3.11-slim

# Metadata
LABEL maintainer="Manus AI"
LABEL description="Automated Trading System Backend"
LABEL version="1.0.0"

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app
ENV FLASK_APP=backend/main_simple.py
ENV FLASK_ENV=production

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        gcc \
        g++ \
        libc6-dev \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY backend/ ./backend/
COPY docs/ ./docs/
COPY .env.example .

# Create necessary directories
RUN mkdir -p data logs backups

# Set proper permissions
RUN chmod +x backend/*.py

# Create non-root user for security
RUN adduser --disabled-password --gecos '' trading \
    && chown -R trading:trading /app

USER trading

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:5001/api/health || exit 1

# Expose port
EXPOSE 5001

# Run the application
CMD ["python", "backend/main_simple.py"]
