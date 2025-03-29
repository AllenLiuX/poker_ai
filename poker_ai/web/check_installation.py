#!/usr/bin/env python
"""Check if all required dependencies are installed for the poker AI web interface."""
import importlib
import sys
import subprocess
import os

def check_python_package(package_name):
    """Check if a Python package is installed."""
    try:
        importlib.import_module(package_name)
        return True
    except ImportError:
        return False

def check_node_installation():
    """Check if Node.js and npm are installed."""
    try:
        node_version = subprocess.run(['node', '--version'], capture_output=True, text=True)
        npm_version = subprocess.run(['npm', '--version'], capture_output=True, text=True)
        
        if node_version.returncode == 0 and npm_version.returncode == 0:
            return True, node_version.stdout.strip(), npm_version.stdout.strip()
        return False, None, None
    except FileNotFoundError:
        return False, None, None

def main():
    """Main entry point for the installation checker."""
    print("=" * 50)
    print("Poker AI Web Interface - Installation Check")
    print("=" * 50)
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"Python version: {python_version}")
    
    # Check required Python packages
    required_packages = [
        'flask', 'flask_cors', 'flask_socketio', 'eventlet', 
        'numpy', 'treys', 'uuid'
    ]
    
    missing_packages = []
    for package in required_packages:
        if check_python_package(package):
            print(f"✅ {package} is installed")
        else:
            print(f"❌ {package} is NOT installed")
            missing_packages.append(package)
    
    # Check Node.js and npm
    node_installed, node_version, npm_version = check_node_installation()
    if node_installed:
        print(f"✅ Node.js is installed (version {node_version})")
        print(f"✅ npm is installed (version {npm_version})")
    else:
        print("❌ Node.js and/or npm are NOT installed")
    
    # Check if frontend dependencies are installed
    frontend_dir = os.path.join(os.path.dirname(__file__), 'frontend')
    node_modules_exist = os.path.exists(os.path.join(frontend_dir, 'node_modules'))
    
    if node_modules_exist:
        print("✅ Frontend dependencies are installed")
    else:
        print("❌ Frontend dependencies are NOT installed")
    
    # Print summary
    print("\n" + "=" * 50)
    print("Installation Check Summary")
    print("=" * 50)
    
    if not missing_packages and node_installed:
        if node_modules_exist:
            print("✅ All dependencies are installed! You're ready to run the web interface.")
            print("\nTo start the web interface, run:")
            print("python poker_ai/web/run_web_interface.py")
        else:
            print("⚠️ Python packages and Node.js are installed, but frontend dependencies are missing.")
            print("\nTo install frontend dependencies, run:")
            print("cd poker_ai/web/frontend && npm install")
    else:
        print("⚠️ Some dependencies are missing. Please install them before running the web interface.")
        
        if missing_packages:
            print("\nMissing Python packages:")
            print(f"pip install {' '.join(missing_packages)}")
        
        if not node_installed:
            print("\nNode.js and npm are required for the frontend:")
            print("Visit https://nodejs.org/ to download and install Node.js")

if __name__ == "__main__":
    main()
