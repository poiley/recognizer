# WebSocket Protocol Documentation

## Messages

### Client -> Server

**Start Processing**
```json
{
  "type": "start",
  "data": "base64_encoded_pdf_content",
  "final": true,
  "total": 1,
  "current": 1
}
```

**Chunk Upload**
```json
{
  "type": "chunk",
  "data": "base64_encoded_chunk",
  "final": false,
  "total": N,
  "current": M
}
```

**Cancel**
```json
{
  "type": "cancel"
}
```

### Server -> Client

**Processing Status**
```json
{
  "status": "processing",
  "current_page": 1,
  "total_pages": 10,
  "progress": 0.5
}
```

**Analysis Status**
```json
{
  "status": "analyzing",
  "current_chunk": 1,
  "total_chunks": 8,
  "progress": 0.125,
  "estimated_time": "4m"
}
```

**Events**
```json
{
  "warning": "string",     // Memory/processing warnings
  "error": "string",       // Error messages
  "type": "ping"          // Heartbeat message
}
```

**Completion**
```json
{
  "complete": true,
  "summary": "string"     // Markdown formatted summary
}
```

## Status Types
- `receiving`: File upload in progress
- `processing`: PDF text extraction
- `analyzing`: AI analysis in progress
- `complete`: Processing complete

## Usage Example
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  
  if (data.type === "ping") return; // Ignore heartbeat
  
  if (data.status) {
    switch(data.status) {
      case 'processing':
        updateProgress(data.progress, data.current_page, data.total_pages);
        break;
      case 'analyzing':
        updateAnalysis(data.progress, data.current_chunk, data.total_chunks, data.estimated_time);
        break;
    }
  }
  
  if (data.complete) handleComplete(data.summary);
  if (data.error) handleError(data.error);
  if (data.warning) handleWarning(data.warning);
};
```

## Connection States
- `CONNECTING`: 0
- `OPEN`: 1
- `CLOSING`: 2
- `CLOSED`: 3

## Error Recovery
- Auto-reconnect on disconnect with exponential backoff (3 attempts)
- Heartbeat monitoring with 7s interval (30s during analysis)
- Maximum missed heartbeats: 3 (10 during analysis)