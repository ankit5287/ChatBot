# Use the official Python image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies needed for some Python packages (like cryptography, etc.)
# and common build tools.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application files (including main.py and .streamlit/config.toml)
COPY . .

# Expose the port that Streamlit runs on (default 8501)
EXPOSE 8501

# Command to run the Streamlit app when the container starts
# We use the port defined in config.toml
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
