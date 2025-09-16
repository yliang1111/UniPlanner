#!/bin/bash

# UniPlanner Server Starter Script
# This script starts both the Django backend and React frontend servers

echo "🚀 Starting UniPlanner Development Servers..."
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check if a port is in use
port_in_use() {
    lsof -i :$1 >/dev/null 2>&1
}

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites found${NC}"

# Check if ports are available
if port_in_use 8000; then
    echo -e "${YELLOW}⚠️  Port 8000 is already in use (Django backend)${NC}"
fi

if port_in_use 3000; then
    echo -e "${YELLOW}⚠️  Port 3000 is already in use (React frontend)${NC}"
fi

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Check if directories exist
if [ ! -d "$BACKEND_DIR" ]; then
    echo -e "${RED}❌ Backend directory not found: $BACKEND_DIR${NC}"
    exit 1
fi

if [ ! -d "$FRONTEND_DIR" ]; then
    echo -e "${RED}❌ Frontend directory not found: $FRONTEND_DIR${NC}"
    exit 1
fi

# Function to start backend server
start_backend() {
    echo -e "${BLUE}🐍 Starting Django Backend Server...${NC}"
    cd "$BACKEND_DIR"
    
    # Check if virtual environment exists
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
        python3 -m venv venv
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Check if dependencies are installed
    if [ ! -f "venv/pyvenv.cfg" ] || ! python -c "import django" 2>/dev/null; then
        echo -e "${YELLOW}⚠️  Installing Python dependencies...${NC}"
        pip install django djangorestframework django-cors-headers python-decouple
    fi
    
    # Run migrations if needed
    echo -e "${BLUE}📊 Checking database migrations...${NC}"
    python manage.py makemigrations --check >/dev/null 2>&1
    if [ $? -ne 0 ]; then
        echo -e "${YELLOW}⚠️  Running database migrations...${NC}"
        python manage.py makemigrations
        python manage.py migrate
    fi
    
    # Start Django server
    echo -e "${GREEN}✅ Django server starting on http://127.0.0.1:8000${NC}"
    python manage.py runserver &
    BACKEND_PID=$!
    echo $BACKEND_PID > .backend_pid
}

# Function to start frontend server
start_frontend() {
    echo -e "${BLUE}⚛️  Starting React Frontend Server...${NC}"
    cd "$FRONTEND_DIR"
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo -e "${YELLOW}⚠️  Installing Node.js dependencies...${NC}"
        npm install
    fi
    
    # Start React server
    echo -e "${GREEN}✅ React server starting on http://localhost:3000${NC}"
    npm start &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > .frontend_pid
}

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    
    # Kill backend server
    if [ -f "$BACKEND_DIR/.backend_pid" ]; then
        BACKEND_PID=$(cat "$BACKEND_DIR/.backend_pid")
        if kill -0 $BACKEND_PID 2>/dev/null; then
            kill $BACKEND_PID
            echo -e "${GREEN}✅ Backend server stopped${NC}"
        fi
        rm -f "$BACKEND_DIR/.backend_pid"
    fi
    
    # Kill frontend server
    if [ -f "$FRONTEND_DIR/.frontend_pid" ]; then
        FRONTEND_PID=$(cat "$FRONTEND_DIR/.frontend_pid")
        if kill -0 $FRONTEND_PID 2>/dev/null; then
            kill $FRONTEND_PID
            echo -e "${GREEN}✅ Frontend server stopped${NC}"
        fi
        rm -f "$FRONTEND_DIR/.frontend_pid"
    fi
    
    echo -e "${GREEN}🎉 All servers stopped successfully${NC}"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Start servers
start_backend
sleep 3  # Give backend time to start
start_frontend

echo -e "\n${GREEN}🎉 UniPlanner is now running!${NC}"
echo -e "${BLUE}📱 Frontend: http://localhost:3000${NC}"
echo -e "${BLUE}🔧 Backend API: http://127.0.0.1:8000${NC}"
echo -e "${BLUE}👤 Admin Panel: http://127.0.0.1:8000/admin${NC}"
echo -e "\n${YELLOW}Press Ctrl+C to stop all servers${NC}"

# Wait for user to stop servers
wait

