FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps
RUN apt-get update && apt-get install -y build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

# Copy project files
COPY pyproject.toml uv.lock* ./
RUN pip install uv && uv sync --frozen

COPY . .

ENV DJANGO_SETTINGS_MODULE=config.settings

EXPOSE 8000

# Run with uvicorn ASGI server
CMD ["uv", "run", "uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]

