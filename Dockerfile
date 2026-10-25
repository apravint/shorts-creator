FROM python:3.12-slim AS builder

WORKDIR /app

# Install system dependencies: FFmpeg with libass/HarfBuzz and fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    fonts-mukta \
    fonts-noto-core \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY pyproject.toml setup.py README.md requirements.txt /app/
COPY shorts_creator /app/shorts_creator/
COPY assets /app/assets/

RUN pip install --no-cache-dir .[all]

# Set environment
ENV PYTHONUNBUFFERED=1
ENV SHORTS_OUTPUT_DIR=/app/output

WORKDIR /app
ENTRYPOINT ["shorts"]
CMD ["--help"]
