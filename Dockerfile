# Use the official Python image as the base for a stable environment
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /usr/src/app

# Install system dependencies needed for robust deployment (e.g., building certain Python packages)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# --- CUSTOM DEPENDENCY INSTALLATION ---
# Install Streamlit and the core dependencies.
# IMPORTANT: This installs the 'google-genai' client library to match your main.py file.
RUN pip install --no-cache-dir \
    streamlit \
    google-genai \
    requests \
    python-dotenv

# Copy all application files (main.py, .streamlit/config.toml, etc.) to the workdir
COPY . .

# Expose the port that Streamlit runs on (default 8501)
EXPOSE 8501

# FIX for Streamlit behind a proxy (like Render). 
# This tells Streamlit to look for assets starting at the root path.
# IMPORTANT: Ensure this variable is ALSO set on your Render service as an environment variable.
ENV STREAMLIT_SERVER_BASE_URL_PATH="/"

# Command to run the Streamlit app when the container starts.
# We run 'main.py' as confirmed by your repository structure.
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0"]
