# Multi-arch, lightweight Python base image
FROM python:3.11-slim

# Prevent Python from writing .pyc files and enable unbuffered logs
ENV PYTHONDONTWRITEBYTECODE=1 \
	PYTHONUNBUFFERED=1 \
	PIP_NO_CACHE_DIR=1 \
	STREAMLIT_BROWSER_GATHER_USAGE_STATS=false \
	STREAMLIT_SERVER_HEADLESS=true \
	PORT=8080

# System deps (libgomp1 for faiss-cpu; build tools help ensure wheels install cleanly)
RUN apt-get update && apt-get install -y --no-install-recommends \
	build-essential \
	curl \
	git \
	libgomp1 \
	&& rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first for better layer caching
COPY requirements.txt ./
RUN python -m pip install --upgrade pip && \
	pip install -r requirements.txt && \
	python -m spacy download en_core_web_lg

# Copy application code
COPY . .

# Streamlit runs a web server inside the container
EXPOSE 8080

# Start the Streamlit app; App Runner/ECS can pass PORT env var
CMD ["/bin/sh", "-c", "streamlit run app.py --server.port=${PORT} --server.address=0.0.0.0"]

