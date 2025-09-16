#!/usr/bin/env python3
"""
UniPlanner Runner Script
A Python-based server management script for UniPlanner
"""

import os
import sys
import subprocess
import signal
import time
import threading
from pathlib import Path

class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    PURPLE = '\033[0;35m'
    CYAN = '\033[0;36m'
    NC = '\033[0m'  # No Color

class UniPlannerRunner:
    def __init__(self):
        self.script_dir = Path(__file__).parent.absolute()
        self.backend_dir = self.script_dir / "backend"
        self.frontend_dir = self.script_dir / "frontend"
        self.backend_process = None
        self.frontend_process = None
        self.running = False

    def print_banner(self):
        banner = f"""
{Colors.CYAN}
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║                    🎓 UniPlanner Runner 🎓                   ║
║                                                              ║
║              Intelligent Degree Planning System              ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
{Colors.NC}
        """
        print(banner)

    def check_prerequisites(self):
        """Check if required tools are installed"""
        print(f"{Colors.BLUE}🔍 Checking prerequisites...{Colors.NC}")
        
        required_commands = {
            'python3': 'Python 3.9+',
            'node': 'Node.js 16+',
            'npm': 'npm package manager'
        }
        
        missing = []
        for cmd, desc in required_commands.items():
            if not self.command_exists(cmd):
                missing.append(f"{cmd} ({desc})")
        
        if missing:
            print(f"{Colors.RED}❌ Missing required tools:{Colors.NC}")
            for tool in missing:
                print(f"   • {tool}")
            return False
        
        print(f"{Colors.GREEN}✅ All prerequisites found{Colors.NC}")
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
        print(f"{Colors.BLUE}🔌 Checking port availability...{Colors.NC}")
        
        ports = {8000: 'Django Backend', 3000: 'React Frontend'}
        occupied = []
        
        for port, service in ports.items():
            if self.port_in_use(port):
                occupied.append(f"Port {port} ({service})")
        
        if occupied:
            print(f"{Colors.YELLOW}⚠️  Occupied ports:{Colors.NC}")
            for port in occupied:
                print(f"   • {port}")
            return False
        
        print(f"{Colors.GREEN}✅ All ports available{Colors.NC}")
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
        print(f"{Colors.BLUE}🐍 Setting up Django Backend...{Colors.NC}")
        
        os.chdir(self.backend_dir)
        
        # Check virtual environment
        venv_path = self.backend_dir / "venv"
        if not venv_path.exists():
            print(f"{Colors.YELLOW}Creating virtual environment...{Colors.NC}")
            subprocess.run([sys.executable, '-m', 'venv', 'venv'], check=True)
        
        # Activate virtual environment and install dependencies
        if os.name == 'nt':  # Windows
            activate_script = venv_path / "Scripts" / "activate.bat"
            pip_path = venv_path / "Scripts" / "pip"
        else:  # Unix/Linux/macOS
            activate_script = venv_path / "bin" / "activate"
            pip_path = venv_path / "bin" / "pip"
        
        # Install dependencies
        print(f"{Colors.YELLOW}Installing Python dependencies...{Colors.NC}")
        subprocess.run([str(pip_path), 'install', '--upgrade', 'pip'], check=True)
        subprocess.run([str(pip_path), 'install', 
                       'django', 'djangorestframework', 
                       'django-cors-headers', 'python-decouple'], check=True)
        
        # Run migrations
        print(f"{Colors.YELLOW}Setting up database...{Colors.NC}")
        python_path = venv_path / "bin" / "python" if os.name != 'nt' else venv_path / "Scripts" / "python"
        subprocess.run([str(python_path), 'manage.py', 'makemigrations'], check=True)
        subprocess.run([str(python_path), 'manage.py', 'migrate'], check=True)
        
        # Create admin user
        print(f"{Colors.YELLOW}Creating admin user...{Colors.NC}")
        subprocess.run([str(python_path), 'manage.py', 'shell', '-c', 
                       "from django.contrib.auth.models import User; "
                       "User.objects.create_superuser('admin', 'admin@example.com', 'admin123') "
                       "if not User.objects.filter(username='admin').exists() else None"], 
                      check=True)
        
        # Populate sample data
        print(f"{Colors.YELLOW}Populating sample data...{Colors.NC}")
        subprocess.run([str(python_path), 'manage.py', 'populate_sample_data'], check=True)
        
        print(f"{Colors.GREEN}✅ Backend setup complete{Colors.NC}")

    def setup_frontend(self):
        """Setup React frontend"""
        print(f"{Colors.BLUE}⚛️  Setting up React Frontend...{Colors.NC}")
        
        os.chdir(self.frontend_dir)
        
        # Install dependencies
        print(f"{Colors.YELLOW}Installing Node.js dependencies...{Colors.NC}")
        subprocess.run(['npm', 'install'], check=True)
        
        print(f"{Colors.GREEN}✅ Frontend setup complete{Colors.NC}")

    def start_backend(self):
        """Start Django backend server"""
        print(f"{Colors.BLUE}🐍 Starting Django Backend Server...{Colors.NC}")
        
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
        
        print(f"{Colors.GREEN}✅ Django server starting on http://127.0.0.1:8000{Colors.NC}")

    def start_frontend(self):
        """Start React frontend server"""
        print(f"{Colors.BLUE}⚛️  Starting React Frontend Server...{Colors.NC}")
        
        os.chdir(self.frontend_dir)
        
        self.frontend_process = subprocess.Popen(
            ['npm', 'start'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
            bufsize=1
        )
        
        print(f"{Colors.GREEN}✅ React server starting on http://localhost:3000{Colors.NC}")

    def monitor_processes(self):
        """Monitor running processes"""
        def monitor_backend():
            if self.backend_process:
                for line in iter(self.backend_process.stdout.readline, ''):
                    if self.running:
                        print(f"{Colors.PURPLE}[Backend] {line.strip()}{Colors.NC}")
                    else:
                        break
        
        def monitor_frontend():
            if self.frontend_process:
                for line in iter(self.frontend_process.stdout.readline, ''):
                    if self.running:
                        print(f"{Colors.CYAN}[Frontend] {line.strip()}{Colors.NC}")
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
        print(f"\n{Colors.YELLOW}🛑 Shutting down servers...{Colors.NC}")
        self.stop_servers()
        sys.exit(0)

    def stop_servers(self):
        """Stop all running servers"""
        self.running = False
        
        if self.backend_process:
            self.backend_process.terminate()
            print(f"{Colors.GREEN}✅ Backend server stopped{Colors.NC}")
        
        if self.frontend_process:
            self.frontend_process.terminate()
            print(f"{Colors.GREEN}✅ Frontend server stopped{Colors.NC}")

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
                print(f"{Colors.RED}❌ Setup failed: {e}{Colors.NC}")
                return False
        
        # Check ports
        if not self.check_ports():
            print(f"{Colors.YELLOW}⚠️  Some ports are occupied. Continuing anyway...{Colors.NC}")
        
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
            
            print(f"\n{Colors.GREEN}🎉 UniPlanner is now running!{Colors.NC}")
            print(f"{Colors.BLUE}📱 Frontend: http://localhost:3000{Colors.NC}")
            print(f"{Colors.BLUE}🔧 Backend API: http://127.0.0.1:8000{Colors.NC}")
            print(f"{Colors.BLUE}👤 Admin Panel: http://127.0.0.1:8000/admin{Colors.NC}")
            print(f"\n{Colors.YELLOW}Press Ctrl+C to stop all servers{Colors.NC}")
            
            # Wait for processes
            if self.backend_process:
                self.backend_process.wait()
            if self.frontend_process:
                self.frontend_process.wait()
                
        except KeyboardInterrupt:
            self.signal_handler(signal.SIGINT, None)
        except Exception as e:
            print(f"{Colors.RED}❌ Error: {e}{Colors.NC}")
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
