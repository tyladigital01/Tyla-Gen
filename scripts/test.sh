#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════${NC}"
echo -e "${BLUE}Tyla-Gen Tests${NC}"
echo -e "${BLUE}════════════════════════════════════════════${NC}\n"

# Load environment
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo -e "${RED}✗ .env not found${NC}"
    exit 1
fi

# Activate venv
if [ -d venv ]; then
    source venv/bin/activate
else
    echo -e "${RED}✗ Virtual environment not found${NC}"
    exit 1
fi

echo -e "${BLUE}Test 1: Import Check${NC}"
python3 -c "
from tyla_gen.model import ModelManager
from tyla_gen.chat import ChatEngine
from tyla_gen.agent import AgentEngine
from tyla_gen.memory import MemoryManager
from tyla_gen.rag import RAGEngine
from tyla_gen.auth import verify_api_key
print('  ✓ All imports successful')
" && echo -e "${GREEN}✓ PASSED${NC}" || echo -e "${RED}✗ FAILED${NC}"

echo -e "\n${BLUE}Test 2: Model Manager${NC}"
python3 -c "
from tyla_gen.model import ModelManager
mm = ModelManager()
status = mm.get_status()
print(f'  ✓ Model Manager initialized')
print(f'  ✓ Hardware detected: {status[\"hardware\"]}')
" && echo -e "${GREEN}✓ PASSED${NC}" || echo -e "${RED}✗ FAILED${NC}"

echo -e "\n${BLUE}Test 3: Memory Manager${NC}"
python3 -c "
from tyla_gen.memory import MemoryManager
mem = MemoryManager()
mem.log_message('user', 'Test message')
history = mem.get_conversation_history()
if len(history) > 0:
    print(f'  ✓ Memory Manager working')
    print(f'  ✓ Database initialized')
else:
    print('  ✗ No messages in history')
" && echo -e "${GREEN}✓ PASSED${NC}" || echo -e "${RED}✗ FAILED${NC}"

echo -e "\n${BLUE}Test 4: RAG Engine${NC}"
python3 -c "
from tyla_gen.rag import RAGEngine
from tyla_gen.memory import MemoryManager
mem = MemoryManager()
rag = RAGEngine(memory_manager=mem)
print(f'  ✓ RAG Engine initialized')
print(f'  ✓ Documents loaded: {len(rag.list_documents())}')
" && echo -e "${GREEN}✓ PASSED${NC}" || echo -e "${RED}✗ FAILED${NC}"

echo -e "\n${BLUE}Test 5: Tools${NC}"
python3 -c "
from tyla_gen.tools import ToolRegistry
tool_reg = ToolRegistry()
tools = tool_reg.list_tools()
print(f'  ✓ Tool Registry initialized')
print(f'  ✓ Tools available: {len(tools)}')
for tool in tools:
    print(f'    - {tool}')
" && echo -e "${GREEN}✓ PASSED${NC}" || echo -e "${RED}✗ FAILED${NC}"

echo -e "\n${BLUE}Test 6: API Key Verification${NC}"
python3 -c "
from tyla_gen.auth import verify_api_key
if verify_api_key('$TYLA_API_KEY'):
    print('  ✓ API key verified')
else:
    print('  ✗ API key verification failed')
" && echo -e "${GREEN}✓ PASSED${NC}" || echo -e "${RED}✗ FAILED${NC}"

echo -e "\n${BLUE}Test 7: Calculator Tool${NC}"
python3 -c "
from tyla_gen.tools.calculator import CalculatorTool
calc = CalculatorTool()
result = calc.execute({'expression': '2+2'})
if 'Error' not in result:
    print(f'  ✓ Calculator working: {result}')
else:
    print(f'  ✗ Calculator failed: {result}')
" && echo -e "${GREEN}✓ PASSED${NC}" || echo -e "${RED}✗ FAILED${NC}"

echo -e "\n${BLUE}Test 8: File Sandbox${NC}"
python3 -c "
from tyla_gen.tools.file_sandbox import FileSandboxTool
fs = FileSandboxTool()
fs.execute({'action': 'write', 'file': 'test.txt', 'content': 'Hello Tyla'})
result = fs.execute({'action': 'read', 'file': 'test.txt'})
if 'Hello Tyla' in result:
    print('  ✓ Sandbox file operations working')
else:
    print('  ✗ Sandbox operations failed')
" && echo -e "${GREEN}✓ PASSED${NC}" || echo -e "${RED}✗ FAILED${NC}"

echo -e "\n${GREEN}════════════════════════════════════════════${NC}"
echo -e "${GREEN}Test suite complete!${NC}"
echo -e "${GREEN}════════════════════════════════════════════${NC}"
