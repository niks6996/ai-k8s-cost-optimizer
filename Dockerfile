FROM python:3.12-slim

WORKDIR /app

COPY app/main.py .
COPY app/optimizer.py .
COPY app/metrics.json .

RUN useradd --create-home --uid 10001 optimizer \
    && chown -R optimizer:optimizer /app

USER optimizer

CMD ["python", "main.py"]