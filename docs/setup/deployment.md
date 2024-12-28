# Deployment Guide

## Cloud Deployment

### AWS
```bash
aws ecr create-repository --repository-name recognizer-frontend
aws ecr create-repository --repository-name recognizer-backend

# Push images
aws ecr get-login-password | docker login --username AWS --password-stdin $ECR_URI
docker tag frontend:latest $ECR_URI/recognizer-frontend
docker tag backend:latest $ECR_URI/recognizer-backend
docker push $ECR_URI/recognizer-frontend
docker push $ECR_URI/recognizer-backend
```

### Docker Compose (Production)
```yaml
version: '3.8'
services:
  frontend:
    image: $ECR_URI/recognizer-frontend
    restart: always
    environment:
      - NODE_ENV=production
  backend:
    image: $ECR_URI/recognizer-backend
    restart: always
```

## Environment Variables
```env
NODE_ENV=production
BACKEND_URL=https://api.yourdomain.com
MAX_MEMORY_PERCENT=80
MAX_WORKERS=4
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