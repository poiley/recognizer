#!/bin/bash

# Use exported versions or get them if not set
if [ -z "$FE_VERSION" ]; then
    export FE_VERSION=$(node -p "require('./frontend/package.json').version")
fi
if [ -z "$BE_VERSION" ]; then
    export BE_VERSION=$(cat backend/version)
fi

docker-compose down

docker rmi recognizer-frontend:latest recognizer-backend:latest recognizer-ollama:latest 2>/dev/null || true
docker rmi frontend:${FE_VERSION}-snapshot backend:${BE_VERSION}-snapshot 2>/dev/null || true

exit 0