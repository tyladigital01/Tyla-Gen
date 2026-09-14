# Tyla-Gen 🧠

**All-in-One AI Server Running Directly Inside GitHub Codespaces**

Tyla-Gen is a self-contained AI system that runs entirely within GitHub Codespaces. No external APIs. No cloud dependencies. Just pure local inference with a full-featured API, chatbot, agent mode, and web UI.

## Features

✅ **Local Model Inference** - Runs quantized open-source models (Phi-2, Mistral, etc.)  
✅ **FastAPI Server** - Full REST API with authentication  
✅ **Chatbot Mode** - Conversational AI powered by local model  
✅ **Agent Mode** - Controlled tool use with reasoning  
✅ **Web UI** - Interactive interface served from Codespace  
✅ **CLI** - Command-line interface for interaction  
✅ **Memory** - SQLite-based persistent storage  
✅ **RAG** - Local knowledge retrieval (TXT, Markdown, JSON)  
✅ **Hardware Detection** - Automatically selects model based on Codespace specs  
✅ **Public Access** - Forwarded Codespace URL for remote access  
✅ **Ethical Framework** - Owner-restricted, sandbox-isolated tool execution  

## Quick Start

### 1. Open in Codespaces

Click "Code" → "Codespaces" → "Create codespace on main"

### 2. Setup

```bash
./scripts/setup.sh
```

This will:
- Detect your hardware
- Create Python virtual environment
- Install dependencies
- Download and verify the model
- Prepare database and sandbox
- Run tests

### 3. Start Tyla-Gen

```bash
./scripts/start.sh
```

You'll see:
```
✓ Model loaded: phi-2 (4.7GB quantized)
✓ FastAPI running on http://0.0.0.0:8000
✓ Codespace public URL: https://user-xxxx.github.dev:8000
```

### 4. Access

- **Web UI**: Open the forwarded port URL in your browser
- **API**: Send requests to `https://your-codespace-url/v1/chat/completions`
- **CLI**: `tyla chat "Your message"`

## Architecture

```
Client (Browser/CLI/External)
  ↓
FastAPI Server (8000)
  ↓
Tyla-Gen Core
  ├── Chatbot Engine
  ├── Agent Engine (Tool Controller)
  ├── Memory (SQLite)
  └── RAG System
  ↓
Inference Engine (llama.cpp / ONNX)
  ↓
Local Model (Phi-2 or Mistral)
```

## API Endpoints

### Health & Status
```bash
GET /health
GET /v1/status
GET /v1/models
```

### Chat Completions
```bash
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "messages": [
    {"role": "user", "content": "Explain JWT tokens"}
  ],
  "temperature": 0.7,
  "max_tokens": 2048
}
```

### Agent Mode
```bash
POST /v1/agent
Content-Type: application/json
Authorization: Bearer YOUR_API_KEY

{
  "task": "Calculate the sum of 42 and 58",
  "tools": ["calculator", "http_request"]
}
```

## CLI Usage

```bash
# Chat mode
tyla chat "What is ethical hacking?"

# Agent mode
tyla agent "Analyze this JSON file" --file data.json

# Status
tyla status

# List models
tyla models

# Set API URL
export TYLA_API_URL=https://your-codespace-url
```

## Ethical Hacking Learning

Tyla-Gen supports learning ethical hacking concepts through:

1. **Knowledge Base** - Upload security research papers, OWASP guidelines, etc.
2. **Controlled Execution** - Tools are sandboxed and restricted to owner
3. **Reasoning Chain** - Agent explains its decisions step-by-step
4. **Audit Trail** - All interactions logged in memory database

### Safe Tools for Security Learning

- `http_analyzer` - Analyze HTTP requests/responses
- `json_decoder` - Decode and analyze data structures
- `text_analysis` - Pattern detection and cryptanalysis
- `hash_calculator` - Compute common hash functions (educational)
- `base64_converter` - Encode/decode base64
- `regex_matcher` - Pattern matching for security analysis

**Restricted**: Shell access, file system write (outside sandbox), arbitrary network requests

## Hardware Requirements

**Codespace Default**: 2-4 CPU cores, 8GB RAM, 32GB storage

Tyla-Gen will:
1. Detect available resources
2. Select appropriate model (Phi-2 ~4.7GB for small hardware, Mistral 7B ~7GB for larger)
3. Fail clearly if insufficient resources
4. Never silently fall back to external APIs

## Environment Variables

Create `.env` from `.env.example`:

```bash
cp .env.example .env
# Edit with your settings
```

**Critical**: `TYLA_API_KEY` must be set before starting.

## Project Structure

```
Tyla-Gen/
├── scripts/
│   ├── setup.sh          # One-time setup
│   ├── start.sh          # Start server
│   ├── test.sh           # Run tests
│   └── status.sh         # Check status
├── tyla_gen/
│   ├── main.py           # FastAPI app
│   ├── model.py          # Model loading
│   ├── inference.py      # Inference engine
│   ├── chat.py           # Chatbot logic
│   ├── agent.py          # Agent logic
│   ├── tools/            # Tool implementations
│   ├── memory.py         # SQLite memory
│   ├── rag.py            # RAG engine
│   └── auth.py           # API authentication
├── tyla_cli/
│   └── cli.py            # CLI implementation
├── web/
│   ├── index.html        # Web UI
│   ├── chat.js           # Chat interface
│   └── styles.css        # TYLA blue theme
├── models/
│   └── .gitkeep          # Models downloaded here
├── knowledge/
│   └── .gitkeep          # RAG documents
├── data/
│   └── .gitkeep          # Database and logs
├── sandbox/
│   └── .gitkeep          # Sandboxed file operations
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Security & Safety

✓ **API Key Authentication** - All endpoints require Bearer token  
✓ **Sandbox Isolation** - File operations restricted to `sandbox/`  
✓ **Tool Whitelisting** - Only approved tools can execute  
✓ **Owner Restriction** - Agent responds only to `TYLA_OWNER_ID`  
✓ **Audit Logging** - All actions logged to database  
✓ **No External Callbacks** - Model responses stay local  

## Limitations

- **Codespace Lifecycle**: Stopping/rebuilding may delete model files (use setup script to restore)
- **Inference Speed**: CPU-based inference slower than GPU (but no GPU in free Codespaces)
- **Model Size**: Limited to ~8GB due to Codespace storage constraints
- **Concurrent Users**: Single Codespace instance; deploy multiple if needed
- **Persistence**: Database persists with Codespace storage

## Troubleshooting

### Model fails to load
```bash
# Check available RAM
free -h

# Check disk space
df -h

# Verify model file
ls -lh models/
```

### API not responding
```bash
# Check if server is running
./scripts/status.sh

# View logs
tail -f data/tyla.log
```

### CLI can't connect
```bash
# Verify API URL
echo $TYLA_API_URL

# Test connection
curl -H "Authorization: Bearer $TYLA_API_KEY" $TYLA_API_URL/health
```

## Contributing

This is a personal AI project. Contributions welcome via issues and PRs.

## License

MIT - Use, modify, and distribute freely.

---

**Built by**: Tyla Digital  
**Hosted on**: GitHub Codespaces  
**Model**: Local quantized LLM  
**API**: FastAPI  
**UI**: React + Vanilla JS  
