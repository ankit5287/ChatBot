# Use the official Python image as the base
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Install system dependencies needed for some Python packages (like cryptography, etc.)
# and common build tools.
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# --- CUSTOM DEPENDENCY INSTALLATION ---
# Pinned installation to guarantee tool compatibility and avoid conflicts.
# The `requests` and `python-dotenv` packages are still needed.
RUN pip install --no-cache-dir \
    streamlit \
    google-generativeai==0.10.0 \
    requests \
    python-dotenv

# Copy all application files (including main.py, .env, .streamlit/config.toml, etc.)
# in one clean step to the workdir.
COPY . .

# Expose the port that Streamlit runs on (default 8501)
EXPOSE 8501

# Setting this ENV variable is the correct fix, but if it fails again, 
# you MUST ensure this environment variable is ALSO set on the Render service itself 
# (in the environment variables section) to the correct path, which is usually just `/`.
ENV STREAMLIT_SERVER_BASE_URL_PATH="/"

# Command to run the Streamlit app when the container starts
# We use the port defined in config.toml
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
