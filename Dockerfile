FROM python:3.12-slim

WORKDIR /app

# Install system dependencies for building and runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY package.json package-lock.json ./
RUN apt-get update && apt-get install -y --no-install-recommends nodejs npm && rm -rf /var/lib/apt/lists/*
RUN npm install

COPY . .
RUN npm run build

EXPOSE 3000
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:3000", "--workers", "2"]
