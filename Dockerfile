FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Copy project files
COPY pyproject.toml uv.lock* ./
RUN pip install uv && uv sync --frozen

COPY . .

EXPOSE 8000

# Run with uvicorn ASGI server (env like DATABASE_URL comes from external .env / runtime)
CMD ["uv", "run", "uvicorn", "config.asgi:application", "--host", "0.0.0.0", "--port", "8000"]

