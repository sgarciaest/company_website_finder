# Use official lightweight Python image
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy app code
COPY app/ ./app

# Set environment variable for Python logging
ENV PYTHONUNBUFFERED=1

# Set default command to run the app
CMD ["python", "app/app.py"]
