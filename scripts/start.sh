#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}Starting Tyla-Gen...${NC}"

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓ Environment loaded${NC}"
else
    echo -e "${RED}✗ .env file not found. Run ./scripts/setup.sh first${NC}"
    exit 1
fi

# Activate venv
if [ ! -d "venv" ]; then
    echo -e "${RED}✗ Virtual environment not found. Run ./scripts/setup.sh first${NC}"
    exit 1
fi

source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Verify model exists
echo -e "\n${YELLOW}→ Verifying model...${NC}"
if ! ls models/*.gguf 1> /dev/null 2>&1; then
    echo -e "${RED}✗ No model found in models/ directory${NC}"
    echo -e "${YELLOW}→ Run ./scripts/setup.sh to download a model${NC}"
    exit 1
fi

MODEL_FILE=$(ls -1 models/*.gguf | head -n 1)
MODEL_SIZE=$(du -h "$MODEL_FILE" | cut -f1)
echo -e "${GREEN}✓ Model ready: $(basename $MODEL_FILE) (${MODEL_SIZE})${NC}"

# Set default host and port
HOST=${TYLA_HOST:-0.0.0.0}
PORT=${TYLA_PORT:-8000}

echo -e "\n${BLUE}═══════════════════════════════════════════════${NC}"
echo -e "${GREEN}Tyla-Gen Server Starting${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════${NC}\n"

echo -e "${BLUE}Configuration:${NC}"
echo -e "  API Key: ${YELLOW}$(echo $TYLA_API_KEY | cut -c1-10)...${NC}"
echo -e "  Host: ${YELLOW}${HOST}${NC}"
echo -e "  Port: ${YELLOW}${PORT}${NC}"
echo -e "  Model: ${YELLOW}$(basename $MODEL_FILE)${NC}"
echo -e "  Model Size: ${YELLOW}${MODEL_SIZE}${NC}"
echo -e "  Engine: ${YELLOW}llama-cpp-python${NC}\n"

echo -e "${BLUE}Access:${NC}"
echo -e "  Local: ${YELLOW}http://localhost:${PORT}${NC}"
echo -e "  API: ${YELLOW}http://localhost:${PORT}/v1/chat/completions${NC}\n"

echo -e "${BLUE}Important:${NC}"
echo -e "  ${YELLOW}Port ${PORT} must be forwarded in GitHub Codespaces PORTS panel${NC}"
echo -e "  Once forwarded, you'll get a public HTTPS URL\n"

echo -e "${GREEN}Starting FastAPI server...${NC}\n"

# Start server
python3 -m tyla_gen.main --host $HOST --port $PORT
