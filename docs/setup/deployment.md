# Deployment Guide

## Environment Setup
Create a production `.env` file:
```bash
# Ports
FRONTEND_PORT=5173
BACKEND_PORT=8000
OLLAMA_PORT=11434

# AI/Processing
OLLAMA_MODEL=mistral
CHUNK_SIZE=3000
TOKEN_ENCODING=cl100k_base
PROMPT_FILE=prompts/default.txt
OLLAMA_MEMORY=12G

# Timeouts
HEALTH_CHECK_TIMEOUT=5.0
OLLAMA_TIMEOUT=30.0
```

## Cloud Deployment

### AWS
```bash
# Get versions for tagging
FE_VERSION=$(node -p "require('./frontend/package.json').version")
BE_VERSION=$(cat backend/version)

# Create repositories
aws ecr create-repository --repository-name recognizer-frontend
aws ecr create-repository --repository-name recognizer-backend

# Push images
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI
docker tag frontend:$FE_VERSION $ECR_URI/recognizer-frontend:$FE_VERSION
docker tag backend:$BE_VERSION $ECR_URI/recognizer-backend:$BE_VERSION
docker push $ECR_URI/recognizer-frontend:$FE_VERSION
docker push $ECR_URI/recognizer-backend:$BE_VERSION
```

### Docker Compose (Production)
```yaml
version: '3.8'
services:
  frontend:
    image: $ECR_URI/recognizer-frontend:${FE_VERSION}
    restart: always
    ports:
      - "${FRONTEND_PORT}:${FRONTEND_PORT}"
    environment:
      - NODE_ENV=production

  backend:
    image: $ECR_URI/recognizer-backend:${BE_VERSION}
    restart: always
    ports:
      - "${BACKEND_PORT}:${BACKEND_PORT}"
    environment:
      - NODE_ENV=production
      - OLLAMA_MODEL=${OLLAMA_MODEL}
      - CHUNK_SIZE=${CHUNK_SIZE}
      - TOKEN_ENCODING=${TOKEN_ENCODING}
      - PROMPT_FILE=${PROMPT_FILE}
      - HEALTH_CHECK_TIMEOUT=${HEALTH_CHECK_TIMEOUT}
      - OLLAMA_TIMEOUT=${OLLAMA_TIMEOUT}
```

## Health Checks
- Frontend: `GET /health`
- Backend: `GET /health`
- WebSocket: `wss://api.yourdomain.com/ws`

## SSL/TLS
Configure with reverse proxy (Nginx example):
```nginx
server {
    listen 443 ssl;
    server_name api.yourdomain.com;
    ssl_certificate /etc/letsencrypt/live/domain/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/domain/privkey.pem;

    location /ws {
        proxy_pass http://backend:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```