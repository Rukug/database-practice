# Official Python image for a small, reproducible container
FROM python:3.12-slim

# Flush logs immediately so Railway can show them
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first so this layer is cached when only app code changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the Flask app, templates, and CSV data into the image
COPY . .

# Railway sets PORT at runtime; app.py also falls back to 5000 locally
CMD ["python", "app.py"]
