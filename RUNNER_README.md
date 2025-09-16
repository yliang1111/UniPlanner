# UniPlanner Runner Files

This directory contains several runner scripts to help you easily manage the UniPlanner development environment.

## 🚀 Quick Start

### Option 1: One-Command Setup & Start
```bash
# First time setup + start servers
./setup.sh && ./start_servers.sh

# Or using Python runner
python run.py --setup
```

### Option 2: Manual Setup
```bash
# 1. Setup environment (first time only)
./setup.sh

# 2. Start servers
./start_servers.sh

# 3. Stop servers when done
./stop_servers.sh
```

## 📁 Runner Files Overview

### Shell Scripts (Unix/Linux/macOS)

#### `setup.sh`
- **Purpose**: Initial environment setup
- **What it does**:
  - Checks prerequisites (Python 3, Node.js, npm)
  - Creates Python virtual environment
  - Installs backend dependencies
  - Sets up database with migrations
  - Creates admin user (admin/admin123)
  - Populates sample data
  - Installs frontend dependencies
  - Makes all scripts executable

#### `start_servers.sh`
- **Purpose**: Start both backend and frontend servers
- **What it does**:
  - Checks prerequisites and port availability
  - Starts Django backend on port 8000
  - Starts React frontend on port 3000
  - Monitors both servers
  - Handles graceful shutdown with Ctrl+C

#### `stop_servers.sh`
- **Purpose**: Stop all running servers
- **What it does**:
  - Stops Django backend server
  - Stops React frontend server
  - Cleans up any remaining processes
  - Removes PID files

### Python Runner

#### `run.py`
- **Purpose**: Advanced Python-based server management
- **Features**:
  - Cross-platform compatibility (Windows, macOS, Linux)
  - Real-time process monitoring
  - Colored output and progress indicators
  - Command-line options
  - Automatic setup and dependency management

**Usage:**
```bash
# Basic usage
python run.py

# With initial setup
python run.py --setup

# Backend only
python run.py --backend-only

# Frontend only
python run.py --frontend-only
```

### Windows Batch File

#### `start_servers.bat`
- **Purpose**: Windows-compatible server starter
- **What it does**:
  - Checks prerequisites
  - Sets up virtual environment
  - Installs dependencies
  - Starts both servers in separate windows
  - Provides clear status messages

### Package.json Scripts

#### `package.json`
- **Purpose**: npm-style script management
- **Available scripts**:
  ```bash
  npm run setup      # Run initial setup
  npm run start      # Start both servers
  npm run stop       # Stop all servers
  npm run dev        # Start with Python runner
  npm run dev:setup  # Setup + start with Python runner
  npm run backend    # Start backend only
  npm run frontend   # Start frontend only
  npm run clean      # Clean up all generated files
  npm run reset      # Clean + setup (fresh start)
  ```

## 🔧 Prerequisites

### Required Software
- **Python 3.9+**: For Django backend
- **Node.js 16+**: For React frontend
- **npm**: Node package manager

### System Requirements
- **macOS/Linux**: Bash shell support
- **Windows**: Command Prompt or PowerShell
- **Memory**: At least 2GB RAM
- **Disk**: At least 1GB free space

## 📊 Server Information

### Backend Server (Django)
- **URL**: http://127.0.0.1:8000
- **Admin Panel**: http://127.0.0.1:8000/admin
- **API Base**: http://127.0.0.1:8000/api/
- **Default Credentials**: admin/admin123

### Frontend Server (React)
- **URL**: http://localhost:3000
- **Hot Reload**: Enabled
- **Development Mode**: Enabled

## 🛠️ Troubleshooting

### Common Issues

#### Port Already in Use
```bash
# Check what's using the ports
lsof -i :8000  # Backend port
lsof -i :3000  # Frontend port

# Kill processes using the ports
kill -9 $(lsof -ti :8000)
kill -9 $(lsof -ti :3000)
```

#### Permission Denied (macOS/Linux)
```bash
# Make scripts executable
chmod +x *.sh
chmod +x run.py
```

#### Virtual Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf backend/venv
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Node Modules Issues
```bash
# Clean and reinstall
rm -rf frontend/node_modules
cd frontend
npm install
```

#### Database Issues
```bash
# Reset database
rm backend/db.sqlite3
cd backend
source venv/bin/activate
python manage.py migrate
python manage.py populate_sample_data
```

### Error Messages

#### "Command not found"
- Ensure Python 3, Node.js, and npm are installed
- Check that they're in your PATH

#### "Permission denied"
- Make scripts executable: `chmod +x *.sh`
- On Windows, run Command Prompt as Administrator

#### "Port already in use"
- Stop existing servers: `./stop_servers.sh`
- Or kill processes manually using the port numbers

#### "Module not found"
- Run setup: `./setup.sh`
- Or install dependencies manually

## 🔄 Development Workflow

### Daily Development
```bash
# Start servers
./start_servers.sh

# Make changes to code
# Servers auto-reload on file changes

# Stop servers when done
./stop_servers.sh
```

### Fresh Start
```bash
# Clean everything and start fresh
npm run reset
```

### Backend Only Development
```bash
# Start only Django backend
python run.py --backend-only
```

### Frontend Only Development
```bash
# Start only React frontend
python run.py --frontend-only
```

## 📝 Customization

### Changing Ports
Edit the following files to change default ports:

**Backend (Django)**:
- `backend/manage.py runserver 8001` (change 8000 to 8001)

**Frontend (React)**:
- `frontend/package.json`: Add `"start": "PORT=3001 react-scripts start"`
- Or set environment variable: `PORT=3001 npm start`

### Adding New Scripts
Add new scripts to `package.json`:
```json
{
  "scripts": {
    "test": "python backend/manage.py test",
    "lint": "npm run lint --prefix frontend"
  }
}
```

## 🎯 Best Practices

1. **Always use virtual environment** for Python dependencies
2. **Run setup.sh first** on new machines
3. **Use Ctrl+C** to stop servers gracefully
4. **Check logs** if servers fail to start
5. **Keep dependencies updated** regularly
6. **Use version control** for your code changes

## 📞 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Verify all prerequisites are installed
3. Try running `./stop_servers.sh` then `./start_servers.sh`
4. For persistent issues, try `npm run reset`

## 🚀 Production Deployment

These runner files are for **development only**. For production:

1. Use proper web servers (nginx, Apache)
2. Use production databases (PostgreSQL, MySQL)
3. Set up proper environment variables
4. Use process managers (PM2, systemd)
5. Enable HTTPS and security headers

