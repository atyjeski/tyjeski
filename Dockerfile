# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# Install pip requirements
ADD backend/requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
ADD backend /app

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

# run gunicorn
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT