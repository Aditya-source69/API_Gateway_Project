# ── Base image ───────────────────────────────────────────────────────
# Start from an official Python image. "slim" = small (no build tooling we
# don't need), so the final image is lighter and faster to ship.
FROM python:3.10-slim

# ── Working directory ────────────────────────────────────────────────
# Every command below runs from /app inside the container. Our code lands
# here, so paths like "gateway/gateway.log" resolve the same as on your PC.
WORKDIR /app

# ── Install dependencies FIRST (layer caching) ───────────────────────
# We copy ONLY requirements.txt, then install. Docker caches each step as a
# layer. As long as requirements.txt doesn't change, Docker reuses the cached
# install on every rebuild — even when you edit your Python code. Big speedup.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# ── Copy the application code ─────────────────────────────────────────
# Now bring in the rest (gateway/, services/). This layer rebuilds when your
# code changes, but the dependency layer above stays cached.
COPY . .

# ── Document the port ────────────────────────────────────────────────
# EXPOSE is documentation only; it doesn't publish the port. The gateway
# listens on 8000; compose decides what actually gets published to the host.
EXPOSE 8000

# ── Default command ──────────────────────────────────────────────────
# What runs if no command is given. docker-compose.yml overrides this per
# service. CRITICAL: --host 0.0.0.0 (NOT 127.0.0.1) so the server is
# reachable from outside the container. 127.0.0.1 would only accept
# connections from inside the same container — a classic Docker gotcha.
CMD ["uvicorn", "gateway.main:app", "--host", "0.0.0.0", "--port", "8000"]
