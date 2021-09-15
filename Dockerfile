# For more information, please refer to https://aka.ms/vscode-docker-python
FROM python:3.8-slim-buster

# Set work directory
WORKDIR /app
ADD backend /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG 0

# Install dependencies
COPY backend/requirements.txt .
RUN python -m pip install -r requirements.txt

# Copy project
COPY . .

# Switching to a non-root user, please refer to https://aka.ms/vscode-docker-python-user-rights
RUN useradd appuser && chown -R appuser /app
USER appuser

# Collect static files
RUN python manage.py collectstatic --noinput

# Run gunicorn
CMD gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT