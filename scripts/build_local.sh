#!/bin/bash

# Check if docker is running
if ! docker info >/dev/null 2>&1; then
   echo "Docker not running"
   exit 1
fi

# # Check Ollama
# if ! command -v ollama &> /dev/null; then
#     echo "Ollama not installed"
#     exit 1
# fi

# if ! pgrep -x "ollama" > /dev/null; then
#     echo "Ollama not running"
#     exit 1
# fi

# # Check model
# if ! ollama list | grep -q "mistral"; then
#     echo "Pulling Mistral model..."
#     ollama pull mistral
# fi


# Get versions and append snapshot
FE_VERSION=$(cat frontend/version)
BE_VERSION=$(cat backend/version)

# Build frontend
cd frontend || exit
echo "Building frontend ${FE_VERSION}-snapshot..."
docker build -t frontend:${FE_VERSION}-snapshot .

# Build backend
cd ../backend || exit
echo "Building backend ${BE_VERSION}-snapshot..."
docker build -t backend:${BE_VERSION}-snapshot .

cd ..
docker-compose up -d

exit 0