# syntax = docker/dockerfile:1.4

FROM python:3.9-slim AS builder

WORKDIR /app

COPY requirements.txt ./
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install -r requirements.txt

COPY . .

# Imagen final para el entorno de desarrollo
FROM builder AS dev-envs

RUN apt-get update && apt-get install -y --no-install-recommends git

RUN useradd -s /bin/bash -m vscode && groupadd docker && usermod -aG docker vscode

COPY --from=gloursdocker/docker / /

WORKDIR /app

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
