FROM python:3.11-slim

WORKDIR /app

USER root

ENV DEBIAN_FRONTEND noninteractive
ENV API_PORT=8000

EXPOSE $API_PORT

RUN mkdir ./src
COPY poetry.lock pyproject.toml /

RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install curl gcc -y && \
    rm -rf /var/lib/apt/lists/* && \
    pip install poetry && \
    poetry install --without dev


COPY ./src ./src

CMD poetry run uvicorn src.main:app --host 0.0.0.0 --port "$API_PORT"
