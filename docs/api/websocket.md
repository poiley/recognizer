# WebSocket Protocol Documentation

## Messages

### Client -> Server

**Start Processing**
```json
{
  "type": "start",
  "data": "Uint8Array" 
}
```

**Cancel**
```json
{
  "type": "cancel"
}
```

### Server -> Client

**Progress**
```json
{
  "progress": 0.5,
  "page": 1,
  "total": 10
}
```

**Events**
```json
{
  "warning": "string",  // Memory/processing warnings
  "error": "string",    // Error messages
  "complete": true,     // Processing complete
  "summary": "string"   // Markdown formatted summary
}
```

## Usage Example
```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  if (data.error) handleError(data.error);
  if (data.complete) handleComplete(data.summary);
  if (data.progress) updateProgress(data.progress);
};
```

## Connection States
- `CONNECTING`: 0
- `OPEN`: 1
- `CLOSING`: 2
- `CLOSED`: 3

## Error Recovery
Auto-reconnect on disconnect with exponential backoff (3 attempts)