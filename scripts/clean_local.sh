
#!/bin/bash

# Get versions from version files
FE_VERSION=$(cat frontend/version)
BE_VERSION=$(cat backend/version)

docker-compose down

docker rmi recognizer-frontend:latest recognizer-backend:latest recognizer-ollama:latest 2>/dev/null || true
docker rmi frontend:${FE_VERSION}-snapshot backend:${BE_VERSION}-snapshot 2>/dev/null || true

exit 0