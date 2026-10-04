FROM python:3.12-slim@sha256:f77ac9e44ae96ef2c90b8053ea08c31f8be030f824196b0ae4db6d462c84e51f
WORKDIR /work
COPY app/ /work/app/
COPY data/ /work/data/
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/work/app
CMD ["python", "-c", "from store import Store; print('Store import ready')"]
