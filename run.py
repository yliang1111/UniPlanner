#!/usr/bin/env python3
"""
UniPlanner Runner Script
"""

import os
import sys
import subprocess
import signal
import time
import threading
from pathlib import Path

class UniPlannerRunner:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.backend_dir = self.script_dir / "backend"
        self.frontend_dir = self.script_dir / "frontend"
        self.backend_process = None
        self.frontend_process = None
        self.running = False

    def print_banner(self):
        print("UniPlanner - Starting servers...")

    def check_prerequisites(self):
        """Check if required tools are installed"""
        print("Checking prerequisites...")
        
        required_commands = ['python3', 'node', 'npm']
        missing = []
        
        for cmd in required_commands:
            if not self.command_exists(cmd):
                missing.append(cmd)
        
        if missing:
            print(f"Missing required tools: {', '.join(missing)}")
            return False
        
        print("All prerequisites found")
        return True

    def command_exists(self, command):
        """Check if a command exists in PATH"""
        try:
            subprocess.run([command, '--version'], 
                         capture_output=True, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False

    def check_ports(self):
        """Check if required ports are available"""
        print("Checking port availability...")
        
        ports = [8000, 3000]
        occupied = []
        
        for port in ports:
            if self.port_in_use(port):
                occupied.append(port)
        
        if occupied:
            print(f"Occupied ports: {', '.join(map(str, occupied))}")
            return False
        
        print("All ports available")
        return True

    def port_in_use(self, port):
        """Check if a port is in use"""
        try:
            import socket
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1)
                result = s.connect_ex(('localhost', port))
                return result == 0
        except:
            return False

    def setup_backend(self):
        """Setup Django backend"""
        print("Setting up Django Backend...")
        
        os.chdir(self.backend_dir)
        
        # Check virtual environment
        venv_path = self.backend_dir / "venv"
        if not venv_path.exists():
            print("Creating virtual environment...")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        
        # Install dependencies
        if os.name == 'nt':  # Windows
            pip_path = venv_path / "Scripts" / "pip"
            python_path = venv_path / "Scripts" / "python"
        else:  # Unix/Linux/macOS
            pip_path = venv_path / "bin" / "pip"
            python_path = venv_path / "bin" / "python"
        
        print("Installing Python dependencies...")
        subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], check=True)
        subprocess.run([str(pip_path), 'install', 
                       'django', 'djangorestframework', 
                       'django-cors-headers', 'python-decouple'], check=True)
        
        # Run migrations
        print("Setting up database...")
        subprocess.run([str(python_path), 'manage.py', 'makemigrations'], check=True)
        subprocess.run([str(python_path), 'manage.py', 'migrate'], check=True)
        
        print("Backend setup complete")

    def setup_frontend(self):
        """Setup React frontend"""
        print("Setting up React Frontend...")
        
        os.chdir(self.frontend_dir)
        
        # Install dependencies
        print("Installing Node.js dependencies...")
        subprocess.run(['npm', 'install'], check=True)
        
        print("Frontend setup complete")

    def start_backend(self):
        """Start Django backend server"""
        print("Starting Django Backend Server...")
        
        os.chdir(self.backend_dir)
        venv_path = self.backend_dir / "venv"
        python_path = venv_path / "bin" / "python" if os.name != 'nt' else venv_path / "Scripts" / "python"
        
        self.backend_process = subprocess.Popen(
            [str(python_path), 'manage.py', 'runserver'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("Django server starting on http://127.0.0.1:8000")

    def start_frontend(self):
        """Start React frontend server"""
        print("Starting React Frontend Server...")
        
        os.chdir(self.frontend_dir)
        
        self.frontend_process = subprocess.Popen(
            ['npm', 'start'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print("React server starting on http://localhost:3000")

    def monitor_processes(self):
        """Monitor running processes"""
        def monitor_backend():
            if self.backend_process:
                for line in iter(self.backend_process.stdout.readline, ''):
                    if self.running:
                        print(f"[Backend] {line.strip()}")
                    else:
                        break
        
        def monitor_frontend():
            if self.frontend_process:
                for line in iter(self.frontend_process.stdout.readline, ''):
                    if self.running:
                        print(f"[Frontend] {line.strip()}")
                    else:
                        break
        
        # Start monitoring threads
        backend_thread = threading.Thread(target=monitor_backend, daemon=True)
        frontend_thread = threading.Thread(target=monitor_frontend, daemon=True)
        
        backend_thread.start()
        frontend_thread.start()
        
        return backend_thread, frontend_thread

    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print("\nShutting down servers...")
        self.stop_servers()
        sys.exit(0)

    def stop_servers(self):
        """Stop all running servers"""
        self.running = False
        
        if self.backend_process:
            self.backend_process.terminate()
            print("Backend server stopped")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print("Frontend server stopped")

    def run(self, setup=False):
        """Main run method"""
        self.print_banner()
        
        # Check prerequisites
        if not self.check_prerequisites():
            return False
        
        # Setup if requested
        if setup:
            try:
                self.setup_backend()
                self.setup_frontend()
            except subprocess.CalledProcessError as e:
                print(f"Setup failed: {e}")
                return False
        
        # Check ports
        if not self.check_ports():
            print("Some ports are occupied. Continuing anyway...")
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        try:
            # Start servers
            self.running = True
            self.start_backend()
            time.sleep(3)  # Give backend time to start
            self.start_frontend()
            
            # Monitor processes
            self.monitor_processes()
            
            print("\nUniPlanner is now running!")
            print("Frontend: http://localhost:3000")
            print("Backend API: http://127.0.0.1:8000")
            print("Admin Panel: http://127.0.0.1:8000/admin")
            print("\nPress Ctrl+C to stop all servers")
            
            # Wait for processes
            if self.backend_process:
                self.backend_process.wait()
            if self.frontend_process:
                self.frontend_process.wait()
                
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)
        except Exception as e:
            print(f"Error: {e}")
            self.stop_servers()
            return False
        
        return True

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='UniPlanner Server Runner')
    parser.add_argument('--setup', action='store_true', 
                       help='Run initial setup before starting servers')
    parser.add_argument('--backend-only', action='store_true',
                       help='Start only the backend server')
    parser.add_argument('--frontend-only', action='store_true',
                       help='Start only the frontend server')
    
    args = parser.parse_args()
    
    runner = UniPlannerRunner()
    
    if args.backend_only:
        runner.start_backend()
        try:
            runner.backend_process.wait()
        except KeyboardInterrupt:
            runner.stop_servers()
    elif args.frontend_only:
        runner.start_frontend()
        try:
            runner.frontend_process.wait()
        except KeyboardInterrupt:
            runner.stop_servers()
    else:
        runner.run(setup=args.setup)

if __name__ == '__main__':
    main()
