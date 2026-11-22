# Production Dockerfile for NovaCMS
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    default-libmysqlclient-dev \
    pkg-config \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install python dependencies
COPY backend/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY backend/ /app/
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Collect static files
RUN python manage.py collectstatic --no-input

EXPOSE 8000

# Execute entrypoint script using /bin/sh so built-ins work properly
ENTRYPOINT ["/bin/sh", "/app/entrypoint.sh"]
