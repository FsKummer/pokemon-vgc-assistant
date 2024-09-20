FROM python:3.9-slim

ARG DEBIAN_FRONTEND=noninteractive

ENV PYTHONUNBUFFERED 1

ENV AIRFLOW_HOME=/app/airflow

WORKDIR ${AIRFLOW_HOME}

COPY scripts/ scripts/
RUN chmod +x scripts/entrypoint.sh

COPY pyproject.toml poetry.lock ./

RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir poetry

RUN pip install --no-cache-dir --upgrade pip && \
  poetry install --no-dev
