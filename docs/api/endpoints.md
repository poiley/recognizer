# API Documentation

## WebSocket Endpoint `/ws`

Real-time PDF processing and summarization endpoint.

### Connection
```javascript
const ws = new WebSocket('ws://localhost:8000/ws')
```

### Client Messages

#### Start Processing
```json
{
  "type": "start",
  "data": "base64_encoded_pdf_content"
}
```

#### Cancel Processing
```json
{
  "type": "cancel"
}
```

### Server Messages

#### Progress Update
```json
{
  "progress": 0.5,
  "page": 1,
  "total": 10
}
```

#### Warning
```json
{
  "warning": "Memory pressure detected"
}
```

#### Error
```json
{
  "error": "Error message"
}
```

#### Completion
```json
{
  "complete": true,
  "summary": "markdown_formatted_summary"
}
```

### Error Codes
- 1000: Normal closure
- 1001: Processing canceled
- 1011: Server error

### Rate Limits
- Maximum file size: 100MB
- Maximum concurrent connections: 5