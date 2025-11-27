FROM python:3.11-slim

# Ensure Python output is unbuffered and no .pyc files are written
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Install backend Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the backend application code
COPY . .

EXPOSE 5000

# Wait for the MySQL database to be ready, then start the Flask app
CMD ["sh", "-c", "python wait_for_db.py && python app.py"]
