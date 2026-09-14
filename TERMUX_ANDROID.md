# Termux & Android Integration

## Overview

Tyla-Gen can be accessed from Termux (Android terminal) or any Android app using the forwarded Codespace URL. This enables using your Tyla-Gen AI server from your phone.

## Setup on Android/Termux

### Option 1: Using Termux (Recommended)

1. **Install Termux**
   - Install Termux from F-Droid (not Google Play for latest version)
   - Grant storage permissions

2. **Install Required Tools**
   ```bash
   pkg update
   pkg upgrade
   pkg install curl wget python git
   ```

3. **Get Your Codespace URL**
   - Go to https://github.com/codespaces
   - Open your Tyla-Gen Codespace
   - Click the "Ports" tab
   - Port 8000 should show a forwarded HTTPS URL like:
     ```
     https://username-xxxx.github.dev
     ```

4. **Configure Environment Variables in Termux**
   ```bash
   # Create a config file
   mkdir -p ~/.tyla
   nano ~/.tyla/config.sh
   ```
   
   Add:
   ```bash
   export TYLA_API_URL="https://username-xxxx.github.dev"
   export TYLA_API_KEY="your-api-key-here"
   ```
   
   Load it:
   ```bash
   source ~/.tyla/config.sh
   ```

5. **Test Connection**
   ```bash
   curl -H "Authorization: Bearer $TYLA_API_KEY" \
     $TYLA_API_URL/health
   ```

### Option 2: Using REST API from Any App

Any Android app can call Tyla-Gen's HTTP API:

#### Example in Python (Termux)
```python
import requests
import os

API_URL = os.getenv("TYLA_API_URL")
API_KEY = os.getenv("TYLA_API_KEY")

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Chat
response = requests.post(
    f"{API_URL}/v1/chat/completions",
    headers=headers,
    json={
        "messages": [{"role": "user", "content": "Hello Tyla"}],
        "temperature": 0.7,
        "max_tokens": 512
    }
)

print(response.json()["choices"][0]["text"])
```

#### Example in Java/Kotlin (Android Studio)
```kotlin
import okhttp3.*
import com.google.gson.Gson

val client = OkHttpClient()
val apiUrl = System.getenv("TYLA_API_URL")
val apiKey = System.getenv("TYLA_API_KEY")

val requestBody = """
{
  "messages": [{"role": "user", "content": "Hello Tyla"}],
  "temperature": 0.7,
  "max_tokens": 512
}
""".toRequestBody("application/json".toMediaType())

val request = Request.Builder()
    .url("$apiUrl/v1/chat/completions")
    .header("Authorization", "Bearer $apiKey")
    .post(requestBody)
    .build()

val response = client.newCall(request).execute()
val json = Gson().fromJson(response.body?.string(), JsonObject::class.java)
val text = json["choices"][0]["text"].asString
```

#### Example using cURL
```bash
# Set variables
export TYLA_API_URL="https://username-xxxx.github.dev"
export TYLA_API_KEY="your-key-here"

# Health check
curl "$TYLA_API_URL/health"

# Status (requires auth)
curl -H "Authorization: Bearer $TYLA_API_KEY" \
  "$TYLA_API_URL/v1/status"

# Chat completion
curl -X POST \
  -H "Authorization: Bearer $TYLA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is ethical hacking?"}],
    "temperature": 0.7,
    "max_tokens": 1024
  }' \
  "$TYLA_API_URL/v1/chat/completions"

# Agent execution
curl -X POST \
  -H "Authorization: Bearer $TYLA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Calculate 25 * 4",
    "available_tools": ["calculator"]
  }' \
  "$TYLA_API_URL/v1/agent"

# Search knowledge base
curl -H "Authorization: Bearer $TYLA_API_KEY" \
  "$TYLA_API_URL/v1/rag/search?q=SQL%20injection"
```

## Using Tyla-Gen CLI from Termux

If you want to use the Tyla-Gen CLI in Termux:

1. **Install Tyla-Gen CLI in Termux**
   ```bash
   pkg install python
   pip install click requests tabulate colorama
   ```

2. **Copy CLI files to Termux**
   ```bash
   # Or download from GitHub
   git clone https://github.com/tyladigital01/Tyla-Gen.git
   cd Tyla-Gen
   ```

3. **Create wrapper script**
   ```bash
   cat > ~/bin/tyla << 'EOF'
   #!/bin/bash
   source ~/.tyla/config.sh
   python3 -m tyla_cli.cli "$@"
   EOF
   chmod +x ~/bin/tyla
   ```

4. **Use it**
   ```bash
   tyla status
   tyla chat "Hello world"
   tyla agent "Calculate 100 / 5" --tools calculator
   ```

## Web Browser Access from Android

1. **Open Browser**
   - Chrome, Firefox, or any Android browser

2. **Navigate to Your Codespace**
   ```
   https://username-xxxx.github.dev
   ```

3. **Enter Your API Key**
   - When prompted, enter the `TYLA_API_KEY` from your .env

4. **Use the Web UI**
   - Chat Mode
   - Agent Mode
   - See model status
   - View knowledge base documents

## Network Configuration

### From Home WiFi
- No special configuration needed
- Just use the public Codespace URL

### From Mobile Data
- Same as WiFi - uses HTTPS Codespace URL
- Should work from anywhere with internet

### Behind Proxy/Firewall
- GitHub Codespace URLs are public HTTPS
- Most networks allow outbound HTTPS traffic
- If blocked, your network admin may need to whitelist `github.dev`

## Security Considerations

1. **API Key Security**
   - Never share your `TYLA_API_KEY`
   - Treat it like a password
   - Regenerate if compromised
   - Store in secure location in Termux

2. **HTTPS Connection**
   - All Codespace URLs use HTTPS
   - Browser will verify SSL certificate
   - Safe to use over mobile data

3. **Access Control**
   - Only authenticated requests with API key work
   - Health check endpoint is public for testing
   - All other endpoints require Bearer token

4. **Stopping Access**
   - Stop the Codespace to stop API access
   - Or regenerate API key in .env and restart

## Troubleshooting

### Connection Refused
```bash
# Check if URL is correct
curl "$TYLA_API_URL/health"

# Check if Codespace is running
# Go to https://github.com/codespaces and check status
```

### Authentication Failed
```bash
# Verify API key
echo $TYLA_API_KEY

# Check if key is set in .env on Codespace
# Restart Codespace if changed
```

### Slow Responses
- Model inference on CPU is slow (30-60 seconds typical)
- Wait longer for responses
- Reduce max_tokens if needed

### SSL Certificate Error
- Make sure you're using HTTPS, not HTTP
- GitHub Codespace URLs are always HTTPS
- Browser should automatically verify certificate

## Examples

### Chat About Ethical Hacking
```bash
curl -X POST \
  -H "Authorization: Bearer $TYLA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{
      "role": "user",
      "content": "Explain SQL injection vulnerabilities and how to prevent them"
    }],
    "temperature": 0.7,
    "max_tokens": 2048
  }' \
  "$TYLA_API_URL/v1/chat/completions"
```

### Analyze Security Concept with Agent
```bash
curl -X POST \
  -H "Authorization: Bearer $TYLA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Analyze OWASP A01:2021 Broken Access Control and explain prevention strategies"
  }' \
  "$TYLA_API_URL/v1/agent"
```

### Calculator via Agent
```bash
curl -X POST \
  -H "Authorization: Bearer $TYLA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "task": "Calculate the result of 2^10 + 50",
    "available_tools": ["calculator"]
  }' \
  "$TYLA_API_URL/v1/agent"
```

## Next Steps

1. Start Tyla-Gen Codespace
2. Get the forwarded HTTPS URL
3. Set TYLA_API_URL and TYLA_API_KEY in Termux
4. Test with `curl $TYLA_API_URL/health`
5. Start using from your Android device!

## Notes

- Codespace must be running for API to be accessible
- You can set inactivity timeout in Codespace settings
- Default is 30 minutes (will auto-stop)
- Restart by opening the Codespace again
- Model stays loaded while Codespace is running
