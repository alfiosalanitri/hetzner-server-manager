# Dockerfile

# 1: Build Frontend Assets
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
COPY tailwind.config.js ./
RUN npm install
COPY templates/ ./templates/
COPY static/src/ ./static/src/
RUN npm run build


# 2: Build Final Python Application
FROM python:3.11-slim
WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY --from=builder /app/static/dist ./static/dist/

COPY . .

RUN chmod +x entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]

EXPOSE 5000

CMD ["gunicorn", "--workers", "4", "--bind", "0.0.0.0:5000", "app:app"]