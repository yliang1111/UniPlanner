#!/bin/bash

# UniPlanner Server Stopper Script
# This script stops both the Django backend and React frontend servers

echo "🛑 Stopping UniPlanner Development Servers..."
echo "============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Function to kill process by PID file
kill_by_pid_file() {
    local pid_file="$1"
    local service_name="$2"
    
    if [ -f "$pid_file" ]; then
        local pid=$(cat "$pid_file")
        if kill -0 $pid 2>/dev/null; then
            kill $pid
            echo -e "${GREEN}✅ $service_name server stopped (PID: $pid)${NC}"
        else
            echo -e "${YELLOW}⚠️  $service_name server was not running${NC}"
        fi
        rm -f "$pid_file"
    else
        echo -e "${YELLOW}⚠️  No PID file found for $service_name${NC}"
    fi
}

# Function to kill processes by port
kill_by_port() {
    local port="$1"
    local service_name="$2"
    
    local pids=$(lsof -ti :$port 2>/dev/null)
    if [ -n "$pids" ]; then
        echo "$pids" | xargs kill
        echo -e "${GREEN}✅ $service_name server stopped (Port: $port)${NC}"
    else
        echo -e "${YELLOW}⚠️  No $service_name server found on port $port${NC}"
    fi
}

# Stop backend server
echo -e "${BLUE}🐍 Stopping Django Backend Server...${NC}"
kill_by_pid_file "$BACKEND_DIR/.backend_pid" "Backend"
kill_by_port 8000 "Backend"

# Stop frontend server
echo -e "${BLUE}⚛️  Stopping React Frontend Server...${NC}"
kill_by_pid_file "$FRONTEND_DIR/.frontend_pid" "Frontend"
kill_by_port 3000 "Frontend"

# Additional cleanup - kill any remaining Django/React processes
echo -e "${BLUE}🧹 Cleaning up any remaining processes...${NC}"

# Kill Django processes
pkill -f "manage.py runserver" 2>/dev/null && echo -e "${GREEN}✅ Django processes cleaned up${NC}"

# Kill React processes
pkill -f "react-scripts start" 2>/dev/null && echo -e "${GREEN}✅ React processes cleaned up${NC}"

echo -e "\n${GREEN}🎉 All UniPlanner servers have been stopped${NC}"

