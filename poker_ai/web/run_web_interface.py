#!/usr/bin/env python
"""Script to run the poker AI web interface."""
import os
import sys
import subprocess
import time
import webbrowser
import signal
import atexit
import socket
import psutil

# Add the project root to the path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

def is_port_in_use(port):
    """Check if a port is already in use."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def kill_process_on_port(port):
    """Kill the process using the specified port."""
    for proc in psutil.process_iter(['pid', 'name', 'connections']):
        try:
            for conn in proc.connections():
                if conn.laddr.port == port:
                    print(f"Killing process {proc.pid} ({proc.name()}) using port {port}")
                    proc.terminate()
                    proc.wait(timeout=5)
                    return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False

def run_backend():
    """Run the Flask backend server."""
    backend_port = 5001
    
    if is_port_in_use(backend_port):
        print(f"Port {backend_port} is already in use. Attempting to free it...")
        if not kill_process_on_port(backend_port):
            print(f"Could not free port {backend_port}. Please manually close the application using it.")
            sys.exit(1)
        # Give the OS time to release the port
        time.sleep(1)
    
    print("Starting Flask backend server...")
    backend_dir = os.path.join(os.path.dirname(__file__), 'backend')
    backend_process = subprocess.Popen(
        ['python', 'app.py'],
        cwd=backend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Register cleanup function
    atexit.register(lambda: backend_process.terminate())
    
    # Wait for the server to start
    for line in backend_process.stdout:
        print(f"Backend: {line.strip()}")
        if "Running on" in line:
            break
    
    return backend_process

def run_frontend():
    """Run the React frontend development server."""
    frontend_port = 3000
    
    if is_port_in_use(frontend_port):
        print(f"Port {frontend_port} is already in use. Attempting to free it...")
        if not kill_process_on_port(frontend_port):
            print(f"Could not free port {frontend_port}. Please manually close the application using it.")
            sys.exit(1)
        # Give the OS time to release the port
        time.sleep(1)
        
    print("Starting React frontend development server...")
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    
    # Check if node_modules exists, if not, install dependencies
    if not os.path.exists(os.path.join(frontend_dir, 'node_modules')):
        print("Installing frontend dependencies...")
        subprocess.run(['npm', 'install'], cwd=frontend_dir, check=True)
    
    frontend_process = subprocess.Popen(
        ['npm', 'start'],
        cwd=frontend_dir,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    # Register cleanup function
    atexit.register(lambda: frontend_process.terminate())
    
    # Wait for the server to start
    for line in frontend_process.stdout:
        print(f"Frontend: {line.strip()}")
        if "Compiled successfully" in line or "Starting the development server" in line:
            break
    
    return frontend_process

def main():
    """Main entry point for the web interface runner."""
    print("=" * 50)
    print("Poker AI Web Interface")
    print("=" * 50)
    
    # Start the backend server
    backend_process = run_backend()
    
    # Start the frontend server
    frontend_process = run_frontend()
    
    # Open the web browser
    time.sleep(2)  # Give servers a moment to fully initialize
    webbrowser.open('http://localhost:3000')
    
    print("\nWeb interface is running!")
    print("Backend server: http://localhost:5001")
    print("Frontend server: http://localhost:3000")
    print("\nPress Ctrl+C to stop both servers.")
    
    # Handle graceful shutdown
    def signal_handler(sig, frame):
        print("\nShutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    
    # Keep the script running
    try:
        while True:
            # Print output from the servers
            backend_line = backend_process.stdout.readline()
            if backend_line:
                print(f"Backend: {backend_line.strip()}")
            
            frontend_line = frontend_process.stdout.readline()
            if frontend_line:
                print(f"Frontend: {frontend_line.strip()}")
            
            # Check if either process has terminated
            if backend_process.poll() is not None:
                print("Backend server has stopped. Shutting down...")
                frontend_process.terminate()
                break
            
            if frontend_process.poll() is not None:
                print("Frontend server has stopped. Shutting down...")
                backend_process.terminate()
                break
            
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down servers...")
        backend_process.terminate()
        frontend_process.terminate()

if __name__ == "__main__":
    main()
