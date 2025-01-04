# Local Development Setup

## Prerequisites
- Docker and Docker Compose
- Bun 1.0+
- Python 3.12+
- uv package manager
- Poppler Utils
- Node.js (for version management)

## Quick Start
```bash
# Clone repository
git clone ssh://git@github.com/poiley/recognizer.git

# Build and run with Docker Compose
./scripts/build_local.sh

# Or clean and rebuild everything
./scripts/clean_and_build.sh

# For manual builds:
cd frontend 
bun install
bun run dev

cd ../backend 
pip install uv
uv .venv
source .venv/bin/activate 
uv pip install -r requirements.txt
uvicorn main:app --reload
```

## Environment Variables
The application uses a central `.env` file for configuration:

```bash
# Ports
FRONTEND_PORT=5173
BACKEND_PORT=8000
OLLAMA_PORT=11434

# Versions (automatically managed)
FE_VERSION=1.0.1  # from package.json
BE_VERSION=1.0.1  # from backend/version

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

For local overrides, create a `.env.local` file (gitignored).

## Version Management
- Frontend version is controlled by `package.json`
- Backend version is controlled by `backend/version` file
- Docker images are tagged with respective versions
- Version changes are propagated through environment variables

## Development Commands
```bash
# Frontend
bun run dev         # Development server (default port 5173)
bun run build      # Production build
bun run preview    # Preview production build

# Backend
uvicorn main:app --reload  # Development server (default port 8000)

# Version Management
npm version patch  # Update frontend version
```

## Docker Commands
```bash
# Build images
docker-compose up --build

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Common Issues
- Memory pressure: Adjust OLLAMA_MEMORY in .env
- PDF processing fails: Check Poppler installation
- WebSocket connection fails: Verify CORS settings
- Build fails: Check Bun and Python versions

## Cleanup
```bash
# Remove containers and images
./scripts/clean_local.sh

# Remove dependencies and virtual environments
rm -rf frontend/node_modules backend/venv
```