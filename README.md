# Recognizer

Analyze, summarize, and explain information in PDF textbooks and whitepapers using OCR and AI analysis. Upload PDFs to get markdown summaries and analysis with real-time progress tracking.

## Features
- PDF text extraction with OCR
- Real-time progress tracking
- Chunked file upload
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
- Python 3.11+
- Tesseract OCR
- Poppler Utils

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
npm install
npm run dev

# Backend (default: http://localhost:8000)
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

## Environment Variables
See [Local Setup](docs/setup/local.md#environment-setup) for configuration details.

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
MIT License