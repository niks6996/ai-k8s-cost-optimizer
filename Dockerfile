FROM python:3.12-slim
WORKDIR /workspace
COPY app/requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir --requirement /tmp/requirements.txt
COPY app/ /workspace/app/
ENV PYTHONPATH=/workspace:/workspace/app
RUN groupadd --gid 10001 optimizer \
    && useradd --create-home --uid 10001 --gid 10001 optimizer \
    && chown -R 10001:10001 /workspace
USER 10001:10001
CMD ["python", "app/main.py"]