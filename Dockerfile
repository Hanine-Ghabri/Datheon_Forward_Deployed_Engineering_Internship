FROM python:3.11-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1
WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends build-essential && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY etl ./etl
COPY tests ./tests
RUN useradd --create-home --uid 10001 etluser && mkdir -p /app/data && chown -R etluser:etluser /app
USER etluser
ENTRYPOINT ["python", "-m", "etl.cli"]
