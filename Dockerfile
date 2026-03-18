FROM python:3.11-slim

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       git \
       libxml2-dev \
       libxslt-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

COPY . /app/

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "skiptracer.py"]
