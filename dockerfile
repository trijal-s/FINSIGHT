# ── Base ──────────────────────────────────────────────
FROM python:3.11-slim

# ── Working directory ─────────────────────────────────
WORKDIR /app

# ── System dependencies ───────────────────────────────
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ── Python dependencies ───────────────────────────────
# Copy requirements first — cached until requirements.txt changes
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── App code ──────────────────────────────────────────
COPY src/ ./src/
COPY ui/  ./ui/
COPY data/ ./data/

# ── Expose ports ──────────────────────────────────────
EXPOSE 8000
EXPOSE 8501

# ── Default command ───────────────────────────────────
# Overridden per service in docker-compose.yml
CMD ["python", "src/api.py"]