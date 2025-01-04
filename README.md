# Recognizer

Analyze, summarize, and explain information in PDF textbooks and whitepapers using OCR and AI analysis. Upload PDFs to get markdown summaries and analysis with real-time progress tracking.

## Features
- PDF text extraction with PyMuPDF
- Real-time tracking of analysis progress
- Chunked file upload to Ollama
- Automatic error recovery
- Memory-efficient processing
- Markdown formatted output

## Quick Start
```bash
# Build and run with Docker
./scripts/build_local.sh

# Or clean and rebuild
./scripts/clean_and_build.sh
```

## Requirements
- Docker & Docker Compose
- Node.js 20+
- Python 3.12+
- Bun 1.0+
- uv package manager
- Poppler Utils

## Configuration
The application is configured through a central `.env` file. See [Local Setup](docs/setup/local.md#environment-variables) for details.

Key configuration groups:
- Ports and networking
- Version management
- AI and processing settings
- Timeouts and health checks

## Version Management
- Frontend: Controlled by `package.json`
- Backend: Controlled by `backend/version`
- Images: Tagged with respective component versions

## Documentation
- [API Documentation](docs/api/endpoints.md)
- [WebSocket Protocol](docs/api/websocket.md)
- [Local Development](docs/setup/local.md)
- [Deployment Guide](docs/setup/deployment.md)
- [Architecture Overview](docs/architecture.md)

## Development
```bash
# Frontend (default: http://localhost:5173)
cd frontend
bun install
bun run dev

# Backend (default: http://localhost:8000)
cd backend
pip install uv
uv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License