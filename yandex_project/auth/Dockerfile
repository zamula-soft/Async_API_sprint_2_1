FROM python:3.10-slim-bullseye

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/code

COPY . .

RUN apt update && apt install -y netcat \
    && pip install --no-cache-dir -r requirements.txt \
    && rm -rf /var/lib/apt/lists/* /tmp/* \

#CMD ["gunicorn", "--worker-class", "uvicorn.workers.UvicornWorker", "auth.asgi:asgi_app", "--bind", "0.0.0.0:5000"]