#!/bin/bash

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${BLUE}Tyla-Gen Status${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}\n"

# Check environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓ Environment loaded${NC}"
else
    echo -e "${YELLOW}○ .env not found${NC}"
fi

# Hardware info
echo -e "\n${BLUE}Hardware:${NC}"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "  CPU Cores: ${YELLOW}$(nproc)${NC}"
    echo -e "  RAM: ${YELLOW}$(free -h | awk 'NR==2 {print $2}')${NC}"
    echo -e "  Disk Free: ${YELLOW}$(df -h . | awk 'NR==2 {print $4}')${NC}"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "  CPU Cores: ${YELLOW}$(sysctl -n hw.ncpu)${NC}"
    echo -e "  RAM: ${YELLOW}$(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024))GB${NC}"
    echo -e "  Disk Free: ${YELLOW}$(df -h . | awk 'NR==2 {print $4}')${NC}"
fi

if command -v nvidia-smi &> /dev/null; then
    echo -e "  GPU: ${GREEN}NVIDIA available${NC}"
else
    echo -e "  GPU: ${YELLOW}None (CPU-only)${NC}"
fi

# Model info
echo -e "\n${BLUE}Model:${NC}"
if ls models/*.gguf 1> /dev/null 2>&1; then
    MODEL=$(ls -1 models/*.gguf | head -n 1)
    MODEL_SIZE=$(du -h "$MODEL" | cut -f1)
    echo -e "  File: ${YELLOW}$(basename $MODEL)${NC}"
    echo -e "  Size: ${YELLOW}${MODEL_SIZE}${NC}"
    echo -e "  Engine: ${YELLOW}llama-cpp-python${NC}"
    echo -e "  Status: ${GREEN}Ready${NC}"
else
    echo -e "  File: ${RED}Not found${NC}"
    echo -e "  Status: ${RED}Not loaded${NC}"
fi

# Server status
echo -e "\n${BLUE}Server:${NC}"
if pgrep -f "uvicorn.*tyla_gen" > /dev/null; then
    PORT=$(pgrep -f "uvicorn.*tyla_gen" | xargs ps -o args= | grep -oP ':\K[0-9]+')
    echo -e "  Status: ${GREEN}Running${NC}"
    echo -e "  Port: ${YELLOW}${PORT:-8000}${NC}"
else
    echo -e "  Status: ${YELLOW}Not running${NC}"
    echo -e "  Start with: ${YELLOW}./scripts/start.sh${NC}"
fi

# API info
echo -e "\n${BLUE}API:${NC}"
echo -e "  URL: ${YELLOW}http://localhost:${TYLA_PORT:-8000}${NC}"
echo -e "  Key: ${YELLOW}$(echo ${TYLA_API_KEY:-not set} | cut -c1-10)...${NC}"
echo -e "  Host: ${YELLOW}${TYLA_HOST:-0.0.0.0}${NC}"

# Directory structure
echo -e "\n${BLUE}Directories:${NC}"
echo -e "  Models: ${YELLOW}$(ls -1 models/*.gguf 2>/dev/null | wc -l) file(s)${NC}"
echo -e "  Knowledge: ${YELLOW}$(ls -1 knowledge 2>/dev/null | wc -l) file(s)${NC}"
echo -e "  Sandbox: ${YELLOW}$(ls -1 sandbox 2>/dev/null | wc -l) file(s)${NC}"
echo -e "  Logs: ${YELLOW}$(ls -1 logs 2>/dev/null | wc -l) file(s)${NC}"

echo -e "\n${BLUE}════════════════════════════════════════════${NC}"
