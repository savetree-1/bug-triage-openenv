FROM python:3.11-slim

LABEL maintainer="bug-triage-openenv"
LABEL description="Bug Triage OpenEnv Environment"

# Install curl for healthcheck
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all required files
COPY bug_triage_env/ ./bug_triage_env/
COPY server/ ./server/
COPY openenv.yaml .
COPY inference.py .
COPY README.md .
COPY pyproject.toml .
COPY uv.lock .

# Expose OpenEnv standard port
EXPOSE 8000

# Environment variables
ENV PORT=8000
ENV HOST=0.0.0.0
ENV WORKERS=4
ENV OPENAI_API_KEY=""
ENV GEMINI_API_KEY=""

# Health check
HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:${PORT}/health || exit 1

CMD ["sh", "-c", "uvicorn bug_triage_env.server.app:app --host ${HOST} --port ${PORT} --workers ${WORKERS}"]
