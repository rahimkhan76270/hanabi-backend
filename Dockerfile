# Use the official Python image from Docker Hub
FROM python:3.10-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# COPY .env /app/.env

# Copy the current directory contents into the container at /app
COPY . .
RUN mkdir -p /app/cache && chmod 777 /app/cache
RUN mkdir -p /app/cache/hub
ENV HF_HOME=/app/cache
ENV TRANSFORMERS_CACHE=/app/cache
# Command to run the FastAPI app
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]