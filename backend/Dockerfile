FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y tesseract-ocr poppler-utils
COPY requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-warn-script-location -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--lifespan=on", "--log-level=info"]
