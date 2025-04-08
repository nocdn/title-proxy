# Use an official Python runtime as a parent image (choose a specific version)
FROM python:3.11-slim

# Set environment variables to prevent Python from writing pyc files to disc
ENV PYTHONDONTWRITEBYTECODE 1
# Ensure Python output is sent straight to terminal without being buffered
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies
# --no-cache-dir reduces image size
# --upgrade pip ensures you have the latest pip
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy your application code (the api directory) into the container
COPY ./api ./api

# Expose the port the app runs on *inside* the container (Uvicorn default is 8000)
# This doesn't publish the port, just documents it. Publishing happens in `docker run`.
EXPOSE 8000

# Command to run the application using Uvicorn
# --host 0.0.0.0 makes it accessible from outside the container
# --port 8000 specifies the port inside the container
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8000"]
