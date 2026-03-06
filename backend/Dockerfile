# Backend API for Analytics Dashboard
# Python 3.9+ as per assignment
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Application code (CSV data is bind-mounted at runtime)
COPY main.py .

# Run with uvicorn; host 0.0.0.0 so it's reachable from host
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
