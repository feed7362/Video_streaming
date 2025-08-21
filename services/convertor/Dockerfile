FROM jrottenberg/ffmpeg:7.1-nvidia2204

RUN apt-get update && apt-get install -y  \
    python3.10  \
    python3-pip  \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["python3", "-m", "uvicorn", "rabbit_client:app", "--host", "0.0.0.0", "--port", "8002", "--workers", "4",  "--log-config", "log_conf.yaml"]
