# LLM Query Endpoint - Usage Examples

## 🚀 New POST /llm/query Endpoint

I've successfully implemented a new LLM query endpoint that integrates Google's Gemini API into the Python FastAPI server. Here are the details:

### ✨ Features
- **POST /llm/query** - Accepts text input and returns AI-generated responses
- Uses Google Gemini 1.5-flash model (free tier)
- Includes processing time tracking
- Comprehensive error handling
- CORS enabled for web applications

### 📝 API Specification

**Endpoint:** `POST http://127.0.0.1:8000/llm/query`

**Request Body:**
```json
{
  "text": "Your question or prompt here"
}
```

**Response:**
```json
{
  "response": "AI-generated response text",
  "status": "success",
  "message": "LLM query completed successfully",
  "processing_time": 2.45
}
```

### 🛠 Usage Examples

#### PowerShell
```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/llm/query" -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"text": "Hello, how are you today?"}'
```

#### cURL (Windows)
```cmd
curl -X POST "http://127.0.0.1:8000/llm/query" -H "Content-Type: application/json" -d "{\"text\": \"Explain artificial intelligence\"}"
```

#### Python requests
```python
import requests

response = requests.post(
    "http://127.0.0.1:8000/llm/query",
    headers={"Content-Type": "application/json"},
    json={"text": "Write a haiku about coding"}
)

data = response.json()
print(f"Response: {data['response']}")
print(f"Processing time: {data['processing_time']}s")
```

#### JavaScript (fetch)
```javascript
const response = await fetch('http://127.0.0.1:8000/llm/query', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
    },
    body: JSON.stringify({ text: 'What is machine learning?' })
});

const data = await response.json();
console.log('AI Response:', data.response);
```

### 🧪 Test Results

All tests passed successfully! The endpoint handles various types of queries:

1. **Simple conversations** - "Hello, how are you today?"
2. **Educational explanations** - "Explain artificial intelligence in simple terms"
3. **Creative writing** - "Write a haiku about coding"
4. **Technical questions** - "What are the benefits of using APIs?"
5. **Complex requests** - Recipe creation, problem-solving, etc.

### ⚡ Performance

- Average response time: 1-5 seconds depending on query complexity
- Reliable error handling for API failures
- Proper status codes and error messages

### 🔧 Technical Implementation

- **Framework:** FastAPI with async/await
- **LLM:** Google Gemini 1.5-flash
- **Dependencies:** google-generativeai==0.3.2
- **API Key:** Integrated (configurable via environment variables)
- **CORS:** Enabled for web frontend integration

The endpoint is now live and ready for integration with any frontend application! 🎉

### 🌐 Live Demo

A web interface has been created at `test_llm_web.html` for interactive testing.

---

**Ready to revolutionize your applications with AI-powered responses!** ✨
