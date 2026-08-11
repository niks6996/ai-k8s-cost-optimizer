FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt .
RUN pip install --no-cache-dir --requirement requirements.txt

COPY app/main.py .
COPY app/optimizer.py .
COPY app/kubernetes_metrics.py .
COPY app/metrics.json .

# Use an explicit numeric UID/GID so Kubernetes can verify runAsNonRoot.
RUN groupadd --gid 10001 optimizer \
    && useradd --create-home --uid 10001 --gid 10001 optimizer \
    && chown -R 10001:10001 /app

USER 10001:10001

CMD ["python", "main.py"]