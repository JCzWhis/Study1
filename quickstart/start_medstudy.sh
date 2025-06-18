#!/bin/bash

# 🚀 MedStudy Pro - Quick Start Script (Linux/Mac)
# Inicia todo el sistema en un comando

echo "🏥 MedStudy Pro - Quick Start"
echo "=============================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo -e "${BLUE}📍 Project root: $PROJECT_ROOT${NC}"

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if port is in use
port_in_use() {
    lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null 2>&1
}

# Check dependencies
echo -e "${YELLOW}🔍 Checking dependencies...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js not found. Please install Node.js 16+${NC}"
    exit 1
fi

if ! command_exists ollama; then
    echo -e "${RED}❌ Ollama not found. Please install from ollama.ai${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All dependencies found${NC}"

# Check if ports are available
if port_in_use 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is in use. Backend might already be running.${NC}"
fi

if port_in_use 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 is in use. Frontend might already be running.${NC}"
fi

# Start Ollama service
echo -e "${YELLOW}🤖 Starting Ollama service...${NC}"
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to start
sleep 3

# Check if gemma2:2b is available
if ! ollama list | grep -q "gemma2:2b"; then
    echo -e "${YELLOW}📥 Downloading Gemma2 model (this may take a while)...${NC}"
    ollama pull gemma2:2b
fi

# Start Django backend
echo -e "${YELLOW}🚀 Starting Django backend...${NC}"
cd "$PROJECT_ROOT/medstudy_app"

# Activate virtual environment if it exists
if [ -d "venv_django" ]; then
    source venv_django/bin/activate
    echo -e "${GREEN}✅ Activated Django virtual environment${NC}"
else
    echo -e "${YELLOW}⚠️  No virtual environment found. Run setup first:${NC}"
    echo "python setup_django_medstudy.py"
fi

# Start Django development server
python manage.py runserver 8000 &
DJANGO_PID=$!

# Wait for Django to start
sleep 5

# Start React frontend
echo -e "${YELLOW}🌐 Starting React frontend...${NC}"
cd "$PROJECT_ROOT/frontend"

# Install npm dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}📦 Installing npm dependencies...${NC}"
    npm install
fi

npm start &
FRONTEND_PID=$!

# Wait for frontend to start
sleep 10

# Health checks
echo -e "${YELLOW}🏥 Performing health checks...${NC}"

# Check Django
if curl -s http://localhost:8000/health/ > /dev/null; then
    echo -e "${GREEN}✅ Django backend is running${NC}"
else
    echo -e "${RED}❌ Django backend health check failed${NC}"
fi

# Check frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo -e "${GREEN}✅ React frontend is running${NC}"
else
    echo -e "${RED}❌ React frontend health check failed${NC}"
fi

# Open browser
echo -e "${BLUE}🌍 Opening browser...${NC}"
if command_exists xdg-open; then
    xdg-open http://localhost:3000
elif command_exists open; then
    open http://localhost:3000
else
    echo -e "${YELLOW}Please open http://localhost:3000 in your browser${NC}"
fi

echo ""
echo -e "${GREEN}🎉 MedStudy Pro is now running!${NC}"
echo ""
echo -e "${BLUE}📊 Available interfaces:${NC}"
echo -e "   • Frontend:     http://localhost:3000"
echo -e "   • Django Admin: http://localhost:8000/admin/"
echo -e "   • API Docs:     http://localhost:8000/api/v1/"
echo -e "   • Health Check: http://localhost:8000/health/"
echo ""
echo -e "${YELLOW}💡 Press Ctrl+C to stop all services${NC}"

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down services...${NC}"
    kill $OLLAMA_PID $DJANGO_PID $FRONTEND_PID 2>/dev/null
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup INT TERM

# Wait for user to stop
wait