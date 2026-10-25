# ---------------------------------------------------------------------------
# A Dockerfile is a recipe for building an "image": a sealed box containing
# the app + Python + every library it needs. Run the image and you get a
# "container". It behaves the same on your Mac, on GitHub's servers, or in
# Kubernetes, which is the whole point of Docker.
#
# Build:  docker build -t austin-pipeline:local .
# Run:    docker run -p 8000:8000 austin-pipeline:local
# ---------------------------------------------------------------------------

# 1. Start from an official, small image that already has Python installed.
FROM python:3.12-slim

# 2. Everything below happens inside /app in the container.
WORKDIR /app

# 3. Install libraries FIRST, before copying the code.
#    Docker caches each step. Code changes often, requirements rarely, so this
#    order means rebuilding after a code change skips the slow install step.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Now copy the actual app code in.
COPY app/ ./app/

# 5. Don't run as root inside the container (basic security hygiene).
RUN useradd --create-home appuser
USER appuser

# 6. Which build is this? CI passes the git commit in here; shows up at "/".
ARG APP_VERSION=dev
ENV APP_VERSION=${APP_VERSION}

# 7. Document the port, and the command that starts the server.
EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
