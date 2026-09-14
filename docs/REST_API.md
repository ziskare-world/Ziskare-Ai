# 🌐 Ziskare AI REST API Documentation

The Ziskare AI engine includes a built-in, zero-dependency HTTP REST API microservice.

---

## 🚀 Starting the Server

```powershell
ziskare-ai --server 5005
```

Default endpoint: `http://127.0.0.1:5005`

---

## 📡 Endpoints

### 1. `POST /ask`
Submit a single-shot prompt and receive an immediate direct answer.

**Request**:
```http
POST /ask HTTP/1.1
Host: 127.0.0.1:5005
Content-Type: application/json

{
  "prompt": "What is Docker in one line?",
  "max_new_tokens": 256,
  "temperature": 0.3
}
```

**Response (JSON)**:
```json
{
  "answer": "Docker is an open platform for developing, shipping, and running applications using containers.",
  "time_taken": 0.42,
  "tokens": 21,
  "speed": 50.0
}
```

---

### 2. `POST /chat`
Multi-turn conversational exchange preserving history.

**Request**:
```http
POST /chat HTTP/1.1
Host: 127.0.0.1:5005
Content-Type: application/json

{
  "message": "Remember: user_id is 9982"
}
```

**Response (JSON)**:
```json
{
  "reply": "Noted.",
  "stats": {
    "time_taken": 0.25,
    "tokens": 4,
    "speed": 16.0
  }
}
```

---

### 3. `POST /reset`
Clears chat history back to the initial system prompt.

**Request**:
```http
POST /reset HTTP/1.1
Host: 127.0.0.1:5005
```

**Response (JSON)**:
```json
{
  "status": "memory_reset"
}
```

---

### 4. `GET /health`
Verifies server health and active device.

**Response (JSON)**:
```json
{
  "status": "healthy",
  "service": "Ziskare AI",
  "device": "cuda:0"
}
```
