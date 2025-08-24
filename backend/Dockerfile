# Use an official Python runtime as a parent image
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Add the src directory to the PYTHONPATH
ENV PYTHONPATH "${PYTHONPATH}:/app/src"

# Install system dependencies, INCLUDING CURL for the healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file into the container at /app
COPY ./requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend application code
COPY ./src /app/src
COPY ./fallback /app/fallback

# Make port 8000 available to the world outside this container
EXPOSE 8000

# Run the app. "0.0.0.0" makes it accessible from outside the container.
CMD ["uvicorn", "src.web.main:app", "--host", "0.0.0.0", "--port", "8000"]