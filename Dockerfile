FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt

COPY app/main.py .
COPY app/optimizer.py .
COPY app/kubernetes_metrics.py .
COPY app/metrics.json .

RUN useradd --create-home --uid 10001 optimizer \
    && chown -R optimizer:optimizer /app

USER optimizer

CMD ["python", "main.py"]