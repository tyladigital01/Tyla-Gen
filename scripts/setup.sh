#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}Tyla-Gen Setup Script${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════${NC}"

# Check Python
echo -e "\n${YELLOW}→ Checking Python...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Python 3 not found${NC}"
    exit 1
fi
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo -e "${GREEN}✓ Python ${PYTHON_VERSION}${NC}"

# Detect Hardware
echo -e "\n${YELLOW}→ Detecting hardware...${NC}"
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    CPU_CORES=$(nproc)
    RAM_GB=$(free -g | awk 'NR==2 {print $2}')
    DISK_GB=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
elif [[ "$OSTYPE" == "darwin"* ]]; then
    CPU_CORES=$(sysctl -n hw.ncpu)
    RAM_GB=$(($(sysctl -n hw.memsize) / 1024 / 1024 / 1024))
    DISK_GB=$(($(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//') / 1))
else
    CPU_CORES=2
    RAM_GB=8
    DISK_GB=32
fi

echo -e "${GREEN}✓ CPU Cores: ${CPU_CORES}${NC}"
echo -e "${GREEN}✓ RAM: ${RAM_GB}GB${NC}"
echo -e "${GREEN}✓ Disk: ${DISK_GB}GB${NC}"

# Check GPU
echo -e "\n${YELLOW}→ Checking GPU availability...${NC}"
if command -v nvidia-smi &> /dev/null; then
    echo -e "${GREEN}✓ NVIDIA GPU detected${NC}"
    GPU_AVAILABLE="true"
else
    echo -e "${YELLOW}○ No GPU detected (CPU-only inference)${NC}"
    GPU_AVAILABLE="false"
fi

# Create virtual environment
echo -e "\n${YELLOW}→ Creating Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}"
else
    echo -e "${GREEN}✓ Virtual environment already exists${NC}"
fi

# Activate venv
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip
echo -e "\n${YELLOW}→ Upgrading pip...${NC}"
pip install --upgrade pip --quiet
echo -e "${GREEN}✓ Pip upgraded${NC}"

# Install dependencies
echo -e "\n${YELLOW}→ Installing Python dependencies...${NC}"
pip install -q -r requirements.txt
echo -e "${GREEN}✓ Dependencies installed${NC}"

# Install Tyla-Gen as editable package
echo -e "\n${YELLOW}→ Installing Tyla-Gen CLI...${NC}"
pip install -q -e .
echo -e "${GREEN}✓ Tyla-Gen CLI installed${NC}"

# Create required directories
echo -e "\n${YELLOW}→ Creating directories...${NC}"
mkdir -p models data sandbox knowledge logs
touch models/.gitkeep data/.gitkeep sandbox/.gitkeep knowledge/.gitkeep logs/.gitkeep
echo -e "${GREEN}✓ Directories created${NC}"

# Select and download model based on hardware
echo -e "\n${YELLOW}→ Selecting model based on hardware...${NC}"

if [ $RAM_GB -ge 8 ] && [ $DISK_GB -ge 8 ]; then
    MODEL_NAME="mistral-7b"
    MODEL_URL="https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.1-GGUF/resolve/main/Mistral-7B-Instruct-v0.1.Q4_K_M.gguf"
    MODEL_FILE="mistral-7b.gguf"
    MODEL_SIZE="7.0GB"
    echo -e "${GREEN}✓ Selected: Mistral 7B (7.0GB quantized)${NC}"
elif [ $RAM_GB -ge 6 ] && [ $DISK_GB -ge 6 ]; then
    MODEL_NAME="phi-2"
    MODEL_URL="https://huggingface.co/TheBloke/phi-2-GGUF/resolve/main/phi-2.Q4_K_M.gguf"
    MODEL_FILE="phi-2.gguf"
    MODEL_SIZE="4.7GB"
    echo -e "${GREEN}✓ Selected: Phi-2 (4.7GB quantized)${NC}"
else
    MODEL_NAME="neural-chat"
    MODEL_URL="https://huggingface.co/TheBloke/neural-chat-7B-v3-GGUF/resolve/main/neural-chat-7b-v3.Q4_K_M.gguf"
    MODEL_FILE="neural-chat.gguf"
    MODEL_SIZE="3.5GB"
    echo -e "${GREEN}✓ Selected: Neural Chat (3.5GB quantized)${NC}"
fi

# Download model if needed
echo -e "\n${YELLOW}→ Checking model file...${NC}"
if [ ! -f "models/${MODEL_FILE}" ]; then
    echo -e "${YELLOW}→ Downloading ${MODEL_NAME} (${MODEL_SIZE})...${NC}"
    
    # Check disk space
    REQUIRED_SPACE=$((${MODEL_SIZE%GB} + 2))
    if [ $DISK_GB -lt $REQUIRED_SPACE ]; then
        echo -e "${RED}✗ Insufficient disk space. Need ${REQUIRED_SPACE}GB, have ${DISK_GB}GB${NC}"
        exit 1
    fi
    
    if command -v wget &> /dev/null; then
        wget -q --show-progress -O models/${MODEL_FILE} ${MODEL_URL}
    elif command -v curl &> /dev/null; then
        curl -L -o models/${MODEL_FILE} ${MODEL_URL}
    else
        echo -e "${RED}✗ wget or curl required to download model${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ Model downloaded${NC}"
else
    echo -e "${GREEN}✓ Model already exists${NC}"
fi

# Initialize database
echo -e "\n${YELLOW}→ Initializing database...${NC}"
python3 -c "from tyla_gen.memory import MemoryManager; MemoryManager(); print('✓ Database initialized')"

# Create .env file if it doesn't exist
echo -e "\n${YELLOW}→ Checking environment configuration...${NC}"
if [ ! -f .env ]; then
    echo -e "${YELLOW}→ Creating .env file...${NC}"
    cp .env.example .env
    
    # Generate a random API key
    API_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")
    
    # Update .env with generated key
    if [[ "$OSTYPE" == "darwin"* ]]; then
        sed -i '' "s/TYLA_API_KEY=.*/TYLA_API_KEY=${API_KEY}/" .env
    else
        sed -i "s/TYLA_API_KEY=.*/TYLA_API_KEY=${API_KEY}/" .env
    fi
    
    echo -e "${GREEN}✓ .env file created with random API key${NC}"
else
    echo -e "${GREEN}✓ .env file already exists${NC}"
fi

# Test imports
echo -e "\n${YELLOW}→ Testing imports...${NC}"
python3 -c "from tyla_gen.model import ModelManager; from tyla_gen.chat import ChatEngine; from tyla_gen.agent import AgentEngine; print('✓ All imports successful')"

echo -e "\n${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}Setup complete!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo -e "  1. Review and update .env if needed"
echo -e "  2. Run: ${YELLOW}./scripts/start.sh${NC}"
echo -e "  3. Access the web UI at http://localhost:8000"
echo -e "\n${BLUE}Model Details:${NC}"
echo -e "  Name: ${YELLOW}${MODEL_NAME}${NC}"
echo -e "  File: ${YELLOW}models/${MODEL_FILE}${NC}"
echo -e "  Size: ${YELLOW}${MODEL_SIZE}${NC}"
echo -e "  Engine: ${YELLOW}llama-cpp-python (CPU)${NC}"
echo -e "\n${BLUE}Hardware:${NC}"
echo -e "  CPU Cores: ${YELLOW}${CPU_CORES}${NC}"
echo -e "  RAM: ${YELLOW}${RAM_GB}GB${NC}"
echo -e "  Disk: ${YELLOW}${DISK_GB}GB${NC}"
echo -e "  GPU: ${YELLOW}${GPU_AVAILABLE}${NC}"
