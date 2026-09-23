FROM python:3.12-slim

WORKDIR /app

# faster-whisper/ctranslate2 need libgomp at runtime
RUN apt-get update \
    && apt-get install -y --no-install-recommends libgomp1 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Default process if nothing else is specified (the backend).
# Overridden per-service (e.g. for the Streamlit UI) via `docker run ... <command>`
# or Render's "Docker Command" field.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
