FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DJANGO_SETTINGS_MODULE=ems.settings.production

RUN apt-get update && apt-get install -y \
    build-essential \
    postgresql-client \
    wget \
    curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Collect static files and set permissions
RUN python manage.py collectstatic --noinput && \
    chown -R root:root /app/static /app/staticfiles && \
    chmod -R 755 /app/static /app/staticfiles

EXPOSE 8000

CMD gunicorn ems.wsgi:application --bind 0.0.0.0:8000 --workers 3