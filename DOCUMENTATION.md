# Tyla-Gen Documentation

## Complete Setup & Usage Guide

### Quick Start (5 minutes)

1. **Open GitHub Codespaces**
   ```bash
   # Navigate to Tyla-Gen repository
   # Click Code → Codespaces → Create codespace on main
   ```

2. **Run Setup**
   ```bash
   bash scripts/setup.sh
   ```
   This will:
   - Detect your hardware
   - Create Python environment
   - Download appropriate model
   - Initialize database

3. **Start Server**
   ```bash
   bash scripts/start.sh
   ```

4. **Forward Port**
   - Go to Ports tab in Codespace
   - Right-click port 8000
   - Select "Make Public"
   - Copy the forwarded HTTPS URL

5. **Access**
   - Open browser to your forwarded URL
   - Enter API key from .env
   - Start chatting!

### Environment Setup

After setup.sh, review `.env`:

```bash
cp .env.example .env
# Edit .env and set:
TYLA_API_KEY=your-secure-key
TYLA_PORT=8000
TYLA_HOST=0.0.0.0
```

### API Usage

#### Health Check (Public)
```bash
curl https://your-codespace-url/health
```

#### Status (Requires Auth)
```bash
curl -H "Authorization: Bearer YOUR_API_KEY" \
  https://your-codespace-url/v1/status
```

#### Chat Completion
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "temperature": 0.7,
    "max_tokens": 2048
  }' \
  https://your-codespace-url/v1/chat/completions
```

#### Agent Execution
```bash
curl -X POST \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Calculate 25 * 4",
    "available_tools": ["calculator"]
  }' \
  https://your-codespace-url/v1/agent
```

### CLI Usage

```bash
# Check status
tyla status

# Chat
tyla chat "What is ethical hacking?"

# Agent
tyla agent "Analyze this concept"

# List models
tyla models

# Knowledge base
tyla rag
```

### Web UI

- Access at your Codespace URL
- Chatbot Mode - normal conversation
- Agent Mode - tool-assisted reasoning
- Model Status - hardware and inference info
- Message History - all conversations logged

### Ethical Hacking Learning

Read `knowledge/ETHICAL_HACKING.md` for detailed guide on:
- Networking fundamentals
- Web security (OWASP Top 10)
- Linux security
- Cryptography concepts
- Vulnerability analysis
- CTF challenges
- Authorized penetration testing

### Knowledge Base

Add documents to `knowledge/` directory:
```bash
# Markdown files
knowledge/my-notes.md

# Text files
knowledge/research.txt

# JSON data
knowledge/cves.json
```

Search via API:
```bash
curl -H "Authorization: Bearer KEY" \
  'https://url/v1/rag/search?q=SQL%20injection'
```

### Termux/Android Access

See `TERMUX_ANDROID.md` for detailed instructions on using Tyla-Gen from your phone.

Quick start:
```bash
export TYLA_API_URL="https://your-codespace-url"
export TYLA_API_KEY="your-key"

curl -H "Authorization: Bearer $TYLA_API_KEY" \
  $TYLA_API_URL/health
```

### Monitoring & Logs

```bash
# Check status
bash scripts/status.sh

# View logs
tail -f logs/tyla.log

# Conversation history
# Stored in data/tyla.db (SQLite)
```

### Troubleshooting

#### Model won't load
1. Check available RAM: `free -h`
2. Check disk space: `df -h`
3. Verify model file: `ls -lh models/`
4. Check logs: `tail -f logs/tyla.log`

#### API not responding
1. Check if server is running: `bash scripts/status.sh`
2. Verify port is forwarded in Codespaces
3. Check firewall/network
4. Restart: `bash scripts/start.sh`

#### Slow responses
- Normal for CPU-only inference (30-60 seconds)
- Reduce max_tokens for faster responses
- Consider smaller model if available

#### Authentication fails
1. Verify TYLA_API_KEY is set in .env
2. Copy correct key to authorization header
3. Restart server if .env changed

### Performance Tips

1. **Reduce max_tokens** - Faster responses with smaller outputs
2. **Lower temperature** - More consistent (but slower)
3. **Quantized models** - Use q4_k_m quantization (included)
4. **CPU affinity** - Model uses all available cores

### Security Best Practices

1. **API Key**
   - Keep it secret
   - Treat like password
   - Regenerate if exposed

2. **Codespace**
   - Use branch protection
   - Don't commit .env with real key
   - Use GitHub Secrets for production

3. **Network**
   - HTTPS enforced on Codespace URLs
   - All endpoints require authentication (except /health)
   - API key verified on every request

4. **Data**
   - Conversations stored locally in SQLite
   - No data sent to external services
   - Sandbox prevents unauthorized file access

### Advanced Configuration

#### Custom Model
Edit `tyla_gen/model.py` to add custom model URLs or change quantization.

#### System Prompt
Edit `tyla_gen/chat.py` to customize AI behavior.

#### Tools
Add custom tools in `tyla_gen/tools/` directory.

#### Database
RAW SQL access: `sqlite3 data/tyla.db`

### Support

For issues:
1. Check logs: `tail -f logs/tyla.log`
2. Review README.md
3. Check Codespace terminal for error messages
4. Verify .env configuration

### License

MIT License - Use, modify, and distribute freely.

### Attribution

Built by Tyla Digital for learning ethical hacking and cybersecurity.

Models:
- Phi-2: Microsoft (apache-2.0)
- Mistral-7B: Mistral AI (apache-2.0)
- Neural-Chat: Intel (apache-2.0)

Inference:
- llama-cpp-python (MIT)
- llama.cpp (MIT)

Framework:
- FastAPI (MIT)
- Pydantic (MIT)
- SQLAlchemy (MIT)
