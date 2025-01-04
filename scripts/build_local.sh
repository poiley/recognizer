#!/bin/bash

# Check if docker is running
if ! docker info >/dev/null 2>&1; then
   echo "Docker not running"
   exit 1
fi

# Use exported versions or get them if not set
if [ -z "$FE_VERSION" ]; then
    export FE_VERSION=$(node -p "require('./frontend/package.json').version")
fi
if [ -z "$BE_VERSION" ]; then
    export BE_VERSION=$(cat backend/version)
fi

# Build frontend
cd frontend || exit
echo "Building frontend ${FE_VERSION}..."
docker build -t frontend:${FE_VERSION} . --build-arg VERSION=${FE_VERSION}

# Build backend
cd ../backend || exit
echo "Building backend ${BE_VERSION}..."
docker build -t backend:${BE_VERSION} .

cd ..
docker-compose up -d

exit 0