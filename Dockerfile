# -------- Build stage --------
FROM python:3.12.9-slim AS builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    POETRY_VERSION=1.8.3 \
    POETRY_VIRTUALENVS_CREATE=0

# Install system dependencies required for building packages
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install poetry with the specified version
RUN pip install "poetry==$POETRY_VERSION"

# Set work directory
WORKDIR /application

# Copy poetry configuration files
COPY pyproject.toml poetry.lock* ./

# Install runtime dependencies
RUN poetry install --no-root --no-interaction --no-ansi --only main --without development,testing

# -------- Final stage --------
FROM python:3.12.9-slim AS final

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# Create a non-root user to run the application
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Install runtime system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /application

# Copy installed packages from builder stage
COPY --from=builder /usr/local /usr/local

# Copy application code
COPY --chown=appuser:appuser ./ ./

# Compile Python bytecode
RUN python -m compileall -q

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health-check || exit 1

# Make the entrypoint script executable
RUN chmod +x ./scripts/entrypoint.sh

# Run the application
ENTRYPOINT ["./scripts/entrypoint.sh"]
