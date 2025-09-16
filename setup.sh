#!/bin/bash

# UniPlanner Setup Script
# This script sets up the entire UniPlanner development environment

echo "🔧 Setting up UniPlanner Development Environment..."
echo "=================================================="

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

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Check prerequisites
echo -e "${BLUE}Checking prerequisites...${NC}"

if ! command_exists python3; then
    echo -e "${RED}❌ Python 3 is not installed. Please install Python 3.9+${NC}"
    exit 1
fi

if ! command_exists node; then
    echo -e "${RED}❌ Node.js is not installed. Please install Node.js 16+${NC}"
    exit 1
fi

if ! command_exists npm; then
    echo -e "${RED}❌ npm is not installed. Please install npm${NC}"
    exit 1
fi

echo -e "${GREEN}✅ All prerequisites found${NC}"

# Setup Backend
echo -e "\n${BLUE}🐍 Setting up Django Backend...${NC}"
cd "$BACKEND_DIR"

# Create virtual environment
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating Python virtual environment...${NC}"
    python3 -m venv venv
else
    echo -e "${GREEN}✅ Virtual environment already exists${NC}"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo -e "${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install django djangorestframework django-cors-headers python-decouple

# Run Django migrations
echo -e "${YELLOW}Setting up database...${NC}"
python manage.py makemigrations
python manage.py migrate

# Create superuser if it doesn't exist
echo -e "${YELLOW}Creating admin user...${NC}"
python manage.py shell -c "
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Admin user created: admin/admin123')
else:
    print('Admin user already exists')
"

# Populate sample data
echo -e "${YELLOW}Populating sample data...${NC}"
python manage.py populate_sample_data

echo -e "${GREEN}✅ Backend setup complete${NC}"

# Setup Frontend
echo -e "\n${BLUE}⚛️  Setting up React Frontend...${NC}"
cd "$FRONTEND_DIR"

# Install Node.js dependencies
echo -e "${YELLOW}Installing Node.js dependencies...${NC}"
npm install

echo -e "${GREEN}✅ Frontend setup complete${NC}"

# Make scripts executable
echo -e "\n${BLUE}🔧 Making scripts executable...${NC}"
chmod +x "$SCRIPT_DIR/start_servers.sh"
chmod +x "$SCRIPT_DIR/stop_servers.sh"
chmod +x "$SCRIPT_DIR/setup.sh"

echo -e "${GREEN}✅ Scripts made executable${NC}"

# Final instructions
echo -e "\n${GREEN}🎉 UniPlanner setup complete!${NC}"
echo -e "\n${BLUE}Next steps:${NC}"
echo -e "1. Run ${YELLOW}./start_servers.sh${NC} to start both servers"
echo -e "2. Open ${YELLOW}http://localhost:3000${NC} in your browser"
echo -e "3. Login with ${YELLOW}admin/admin123${NC}"
echo -e "4. Run ${YELLOW}./stop_servers.sh${NC} to stop servers when done"
echo -e "\n${BLUE}Available URLs:${NC}"
echo -e "• Frontend: ${YELLOW}http://localhost:3000${NC}"
echo -e "• Backend API: ${YELLOW}http://127.0.0.1:8000${NC}"
echo -e "• Admin Panel: ${YELLOW}http://127.0.0.1:8000/admin${NC}"

