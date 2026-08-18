FROM python:3.12-slim

WORKDIR /app

COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt

# Keep the complete application package so both the original optimizer
# entrypoint and the Day 22 metrics server can run from the same image.
COPY app/ /app/app/

ENV PYTHONPATH=/app

RUN groupadd --gid 10001 optimizer \
    && useradd --create-home --uid 10001 --gid 10001 optimizer \
    && chown -R 10001:10001 /app

USER 10001:10001

CMD ["python", "app/main.py"]