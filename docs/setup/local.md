# Local Development Setup

## Prerequisites
- Docker and Docker Compose
- Ollama installed and running
- Mistral model pulled (`ollama pull mistral`)
- Node.js 20+
- Python 3.11+
- Github CLI (optional, for artifact pulls)

## Quick Start
```bash
# Clone repository
git clone <repository-url>

# Build and run with Docker
./scripts/local_build.sh


# Or build manually:
cd frontend && npm install
cd ../backend && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt
```

## Environment Variables
```bash
# Frontend (.env)
BACKEND_URL=http://localhost:8000

# Backend (.env)
MAX_MEMORY_PERCENT=80
MAX_WORKERS=2
```

## Development Commands
```bash
# Frontend
npm run dev         # Development server
npm run build      # Production build

# Backend
uvicorn main:app --reload  # Development server
```

## Pulling Artifacts
```bash
export GITHUB_TOKEN=<your-token>
./scripts/pull_latest.sh
```

## Common Issues
- Memory pressure: Adjust MAX_MEMORY_PERCENT
- PDF processing fails: Check Tesseract installation
- WebSocket connection fails: Verify BACKEND_URL

## Cleanup

```bash
./scripts/clean_local.sh # Removes containers and images
```