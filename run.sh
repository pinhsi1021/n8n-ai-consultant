#!/bin/bash

# ANSI Color Codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting n8n AI Consultant setup...${NC}"

# 1. Python Check
if ! command -v python3 &> /dev/null; then
    echo -e "${YELLOW}❌ Python 3 is not installed. Please install Python 3.8+ first.${NC}"
    echo "Download: https://www.python.org/downloads/"
    exit 1
fi

# 2. Virtual Environment Check & Create
if [ ! -d "venv" ]; then
    echo -e "${BLUE}📦 Creating virtual environment (venv)...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}❌ Failed to create venv.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Virtual environment created.${NC}"
else
    echo -e "${GREEN}✅ Virtual environment found.${NC}"
fi

# 3. Connect to venv
source venv/bin/activate

# 4. Install Dependencies
if [ -f "requirements.txt" ]; then
    echo -e "${BLUE}⬇️ Checking and installing dependencies...${NC}"
    pip install -r requirements.txt --quiet
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}❌ Failed to install dependencies.${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Dependencies installed.${NC}"
fi

# 5. Open Browser & Start Server
echo -e "${BLUE}🌐 Opening browser to http://localhost:8080...${NC}"
if [[ "$OSTYPE" == "darwin"* ]]; then
    open "http://localhost:8080"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    xdg-open "http://localhost:8080" 2>/dev/null
fi

echo -e "${GREEN}✅ Server is running! Press Ctrl+C to stop.${NC}"
echo -e "${BLUE}🤖 n8n AI Consultant is ready.${NC}"
python3 web_server.py
