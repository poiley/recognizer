#!/bin/bash

# Use exported versions or get them if not set
if [ -z "$FE_VERSION" ]; then
    export FE_VERSION=$(node -p "require('./frontend/package.json').version")
fi
if [ -z "$BE_VERSION" ]; then
    export BE_VERSION=$(cat backend/version)
fi

docker-compose down

docker rmi frontend:${FE_VERSION} backend:${BE_VERSION} 2>/dev/null || true

exit 0