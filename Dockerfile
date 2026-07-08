# ---- Stage 1: builder — installs dependencies, then is thrown away ----
FROM python:3.10-slim AS builder
WORKDIR /app
COPY requirements.txt .
# Install deps into an isolated prefix we can copy out cleanly
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ---- Stage 2: runtime — the ONLY image that ships ----
FROM python:3.10-slim
WORKDIR /app
# Bring over just the installed packages from the builder — not the build layer itself
COPY --from=builder /install /usr/local
# Copy the application code
COPY . .
# Create a normal (non-root) user, and give it ownership of the app folder.
# (chown is needed because the gateway writes gateway/gateway.log while running,
#  so the non-root user must be allowed to write into /app.)
RUN useradd --create-home --uid 10001 appuser \
    && chown -R appuser:appuser /app

# From here on, everything runs as appuser instead of root.
USER appuser
EXPOSE 8000
# Default command (docker-compose overrides this per service)
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]