FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /opt/app/auth

COPY . .

RUN apt update && apt install -y netcat \
    && pip install --no-cache-dir -r requirements.txt