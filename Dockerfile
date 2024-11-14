FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=box.settings.production

# Install build dsps
RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

#install wget
RUN apt-get update && apt-get install -y wget

#install curl
RUN apt-get update && apt-get install -y curl

# Start Gunicorn
CMD gunicorn box.wsgi:application --bind 0.0.0.0:8000