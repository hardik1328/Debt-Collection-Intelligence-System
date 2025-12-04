#!/usr/bin/env python
"""
Development and deployment utilities
"""
import os
import sys
import subprocess
import json
from pathlib import Path


def install_dependencies():
    """Install Python dependencies"""
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"], check=True)
    print("Dependencies installed!")


def setup_database():
    """Initialize database"""
    print("Setting up database...")
    os.makedirs("data/db", exist_ok=True)
    os.makedirs("data/uploads", exist_ok=True)
    os.makedirs("data/chroma", exist_ok=True)
    
    from app.models.database import create_tables
    from app.core.config import get_settings
    
    settings = get_settings()
    create_tables(settings.database_url)
    print("Database initialized!")


def run_tests():
    """Run test suite"""
    print("Running tests...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-v"], check=True)


def run_dev_server():
    """Run development server"""
    print("Starting development server...")
    subprocess.run([sys.executable, "main.py"])


def build_docker_image():
    """Build Docker image"""
    print("Building Docker image...")
    subprocess.run(["docker", "build", "-t", "contract-intelligence-api:latest", "."], check=True)
    print("Docker image built!")


def start_docker_compose():
    """Start Docker Compose stack"""
    print("Starting Docker Compose...")
    subprocess.run(["docker-compose", "up", "-d"], check=True)
    print("Services started!")


def stop_docker_compose():
    """Stop Docker Compose stack"""
    print("Stopping Docker Compose...")
    subprocess.run(["docker-compose", "down"], check=True)
    print("Services stopped!")


def generate_sample_curl_commands():
    """Generate sample curl commands"""
    commands = {
        "health_check": 'curl http://localhost:8000/admin/healthz',
        "list_documents": 'curl http://localhost:8000/ingest/documents',
        "upload_pdf": 'curl -X POST http://localhost:8000/ingest -F "files=@contract.pdf"',
        "ask_question": '''curl -X POST http://localhost:8000/ask \\
  -H "Content-Type: application/json" \\
  -d '{"question":"What is the payment term?","document_ids":["DOC_ID"]}'
''',
        "run_audit": 'curl -X POST http://localhost:8000/audit?document_id=DOC_ID',
        "get_metrics": 'curl http://localhost:8000/admin/metrics',
    }
    
    print("\nSample curl commands:\n")
    for name, cmd in commands.items():
        print(f"# {name}")
        print(cmd)
        print()


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("""Usage: python utils.py [command]
        
Commands:
  install     - Install Python dependencies
  setup-db    - Initialize database
  tests       - Run test suite
  dev         - Run development server
  docker-build - Build Docker image
  docker-up   - Start Docker Compose
  docker-down - Stop Docker Compose
  examples    - Show sample curl commands
""")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "install":
        install_dependencies()
    elif command == "setup-db":
        setup_database()
    elif command == "tests":
        run_tests()
    elif command == "dev":
        run_dev_server()
    elif command == "docker-build":
        build_docker_image()
    elif command == "docker-up":
        start_docker_compose()
    elif command == "docker-down":
        stop_docker_compose()
    elif command == "examples":
        generate_sample_curl_commands()
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
