# Use Python 3.12 (Required for Django 6.0)
FROM python:3.12-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    gcc \
    curl \
    pkg-config \
    libcairo2-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt /app/

# --- ROBUST FIX: Sanitize requirements using Python ---
# This handles Windows UTF-16 encoding (PowerShell default) which breaks 'sed'.
# We read the file, remove the Windows-only/Problematic packages, and save it back as standard UTF-8.
RUN python -c "import sys, os; \
    raw_data = open('requirements.txt', 'rb').read(); \
    # Detect encoding: Check for UTF-16 BOM (FF FE) \
    encoding = 'utf-16' if raw_data.startswith(b'\xff\xfe') else 'utf-8'; \
    content = raw_data.decode(encoding); \
    # Filter out bad lines \
    lines = [l for l in content.splitlines() if 'pywinpty' not in l and 'pycairo' not in l and 'rlPyCairo' not in l]; \
    # Write back as clean UTF-8 \
    open('requirements.txt', 'w', encoding='utf-8').write('\n'.join(lines))"

# Upgrade pip and install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt && \
    pip install gunicorn whitenoise

# Copy project files
COPY . /app/

# Create a directory for static files
RUN mkdir -p /app/staticfiles

# Expose port 8000
EXPOSE 8000

# Default command
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000"]