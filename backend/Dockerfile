FROM python:3.12-slim
WORKDIR /app

ARG VERSION

LABEL version=$VERSION

# Update pip
RUN pip install --upgrade pip

# Install uv
RUN pip install uv

# Install system dependencies
RUN apt-get update && apt-get install -y poppler-utils

# Copy requirements and install with uv
COPY requirements.txt .
RUN uv pip install --system -r requirements.txt

COPY . .
CMD uvicorn main:app --host 0.0.0.0 --port $BACKEND_PORT --lifespan=on --log-level=info
