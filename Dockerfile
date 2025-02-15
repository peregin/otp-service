# Use the official Python image
FROM python:3.13-slim

# Set environment variables
ENV POETRY_VERSION=1.8.3 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 \
    PATH="$POETRY_HOME/bin:$PATH"

# Install system dependencies
RUN apt-get update && apt-get install -y curl bash && \
    curl -sSL https://install.python-poetry.org | python3 - && \
    apt-get remove -y curl && apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Set the working directory
WORKDIR /app

# Copy only dependency files first for caching
COPY pyproject.toml poetry.lock ./

# Copy the rest of the application
COPY . .

# Install dependencies
RUN /opt/poetry/bin/poetry install --no-root --no-dev

# Expose necessary ports (if applicable)
EXPOSE 5000

# Define the entry point
CMD ["/opt/poetry/bin/poetry", "run", "python", "app.py"]