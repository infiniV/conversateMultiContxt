# syntax=docker/dockerfile:1
ARG PYTHON_VERSION=3.11.6
FROM python:${PYTHON_VERSION}-slim

# Prevents Python from writing pyc files
ENV PYTHONDONTWRITEBYTECODE=1

# Keeps Python from buffering stdout and stderr
ENV PYTHONUNBUFFERED=1

# Create a non-privileged user
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/home/appuser" \
    --shell "/sbin/nologin" \
    --uid "${UID}" \
    appuser

# Install system dependencies including PostgreSQL development libraries
RUN apt-get update && \
    apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    libpq-dev \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Setup working directory
WORKDIR /app

# Install dependencies as root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directories
RUN mkdir -p data/agriculture data/restaurant data/technology data/conversate data/indexes

# Change ownership of the application
RUN chown -R appuser:appuser /app

# Switch to non-root user
USER appuser
ENV BUSINESS_TYPE="agriculture"
ENV ENABLE_FUNCTION_CALLING="true"
ENV ASSISTANT_NAME="Farmovation Assistant"
# Use the built-in download-files argument
RUN python -m src.agent.main download-files

# Run the application
ENTRYPOINT ["python", "-m", "src.agent.main"]
CMD ["start"]