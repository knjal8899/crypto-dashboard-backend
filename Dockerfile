FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install uv first
RUN pip install uv

# Copy project files - use wildcard to handle missing uv.lock gracefully
COPY pyproject.toml ./
COPY uv.lock* ./

# Install dependencies - fallback to pip if uv.lock is missing
RUN if [ -f uv.lock ]; then uv sync --frozen; else uv sync; fi

# Copy rest of the application
COPY . .

EXPOSE 8000

# Run with uvicorn ASGI server
CMD ["uv", "run", "uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]

