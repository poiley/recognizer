# Local Development Setup

## Prerequisites
- Docker and Docker Compose
- Bun 1.0+
- Python 3.11+
- uv package manager
- Poppler Utils
- Github CLI (optional, for artifact pulls)

## Quick Start
```bash
# Clone repository
git clone <repository-url>

# Build and run with Docker Compose
./scripts/build_local.sh

# Or clean and rebuild everything
./scripts/clean_and_build.sh

# For manual builds:
cd frontend 
bun install
bun run dev

cd ../backend 
python -m venv venv 
source venv/bin/activate 
pip install -r requirements.txt
uvicorn main:app --reload
```

## Environment Setup
```bash
# Frontend (.env)
VITE_BACKEND_URL=http://localhost:8000

# Backend (.env)
MAX_MEMORY_PERCENT=80
MAX_WORKERS=2
CORS_ORIGINS=["http://localhost:5173"]
```

## Development Commands
```bash
# Frontend
bun run dev         # Development server (default port 5173)
bun run build      # Production build
bun run preview    # Preview production build

# Backend
uvicorn main:app --reload  # Development server (default port 8000)
```

## Docker Commands
```bash
# Build images
docker build -t frontend:latest frontend/
docker build -t backend:latest backend/

# Run with Docker Compose
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

## Common Issues
- Memory pressure: Adjust MAX_MEMORY_PERCENT in backend environment
- PDF processing fails: Check Poppler installation
- WebSocket connection fails: Verify CORS settings and VITE_BACKEND_URL
- Build fails: Check Bun and Python versions

## Cleanup
```bash
# Remove containers and images
./scripts/clean_local.sh

# Remove dependencies and virtual environments
rm -rf frontend/node_modules backend/venv
```