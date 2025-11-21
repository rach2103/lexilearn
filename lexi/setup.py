#!/usr/bin/env python3
"""
LexiLearn Setup Script
This script helps you set up the LexiLearn application for development.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def print_banner():
    """Print the LexiLearn banner"""
    print("=" * 60)
    print("🎓 LexiLearn - AI Tutor for Dyslexic Students")
    print("=" * 60)
    print("Setting up your development environment...")
    print()

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 9):
        print("❌ Error: Python 3.9 or higher is required")
        print(f"Current version: {sys.version}")
        sys.exit(1)
    print(f"✅ Python {sys.version.split()[0]} detected")

def check_node_version():
    """Check if Node.js is installed"""
    try:
        result = subprocess.run(['node', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Node.js {result.stdout.strip()} detected")
            return True
        else:
            print("❌ Node.js not found")
            return False
    except FileNotFoundError:
        print("❌ Node.js not found")
        return False

def install_backend_dependencies():
    """Install Python backend dependencies"""
    print("\n📦 Installing backend dependencies...")
    
    backend_dir = Path("backend")
    if not backend_dir.exists():
        print("❌ Backend directory not found")
        return False
    
    try:
        # Create virtual environment
        subprocess.run([sys.executable, "-m", "venv", "backend/venv"], check=True)
        
        # Activate virtual environment and install dependencies
        if platform.system() == "Windows":
            pip_path = "backend/venv/Scripts/pip"
        else:
            pip_path = "backend/venv/bin/pip"
        
        subprocess.run([pip_path, "install", "-r", "backend/requirements.txt"], check=True)
        print("✅ Backend dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install backend dependencies: {e}")
        return False

def install_frontend_dependencies():
    """Install Node.js frontend dependencies"""
    print("\n📦 Installing frontend dependencies...")
    
    frontend_dir = Path("frontend")
    if not frontend_dir.exists():
        print("❌ Frontend directory not found")
        return False
    
    try:
        subprocess.run(["npm", "install"], cwd="frontend", check=True)
        print("✅ Frontend dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install frontend dependencies: {e}")
        return False

def create_env_files():
    """Create environment files"""
    print("\n🔧 Creating environment files...")
    
               # Backend .env
    backend_env_content = """# Database Configuration
       DATABASE_URL=postgresql://postgres:prakruthi%402606@localhost:5432/lexilearn
       
       # Redis Configuration
       REDIS_URL=redis://localhost:6379
       
       # Security
       SECRET_KEY=your-secret-key-change-in-production
       ALGORITHM=HS256
       ACCESS_TOKEN_EXPIRE_MINUTES=30
       
       # Speech Processing API Configuration
       # Choose one: "openai", "huggingface", "local_whisper", "google", "azure"
       SPEECH_API_TYPE=local_whisper
       
       # OpenAI Configuration (if using OpenAI)
       OPENAI_API_KEY=your-openai-api-key-here
       
       # Hugging Face Configuration (if using Hugging Face)
       HUGGINGFACE_TOKEN=your-huggingface-token-here
       
       # Google Cloud Configuration (if using Google Cloud)
       GOOGLE_CLOUD_CREDENTIALS=path/to/your/google-credentials.json
       
       # Azure Cognitive Services (if using Azure)
       AZURE_SPEECH_KEY=your-azure-speech-key-here
       AZURE_SPEECH_REGION=your-azure-region-here
       
       # CORS
       ALLOWED_ORIGINS=["http://localhost:3000", "http://127.0.0.1:3000"]
       
       # File Upload
       MAX_FILE_SIZE=10485760
       UPLOAD_DIR=uploads
       
       # ML Models
       MODEL_CACHE_DIR=ml_models/cache
       """
    
    # Frontend .env
    frontend_env_content = """# API Configuration
REACT_APP_API_URL=http://localhost:8000
REACT_APP_WS_URL=ws://localhost:8000/ws

# Environment
REACT_APP_ENV=development
"""
    
    try:
        with open("backend/.env", "w") as f:
            f.write(backend_env_content)
        print("✅ Backend .env file created")
        
        with open("frontend/.env", "w") as f:
            f.write(frontend_env_content)
        print("✅ Frontend .env file created")
        
        return True
    except Exception as e:
        print(f"❌ Failed to create environment files: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating necessary directories...")
    
    directories = [
        "backend/uploads",
        "backend/ml_models/cache",
        "backend/logs"
    ]
    
    try:
        for directory in directories:
            Path(directory).mkdir(parents=True, exist_ok=True)
        print("✅ Directories created successfully")
        return True
    except Exception as e:
        print(f"❌ Failed to create directories: {e}")
        return False

def print_next_steps():
    """Print next steps for the user"""
    print("\n" + "=" * 60)
    print("🎉 Setup completed successfully!")
    print("=" * 60)
    print("\n📋 Next steps:")
    print("1. Install PostgreSQL and Redis:")
    print("   PostgreSQL: https://www.postgresql.org/download/")
    print("   Redis: https://redis.io/download")
    print("   - Create database 'lexilearn' in PostgreSQL")
    print("   - Update DATABASE_URL and REDIS_URL in backend/.env if needed")
    print()
    print("2. Configure your speech processing API:")
    print("   Choose one of these options:")
    print("   a) Hugging Face (Recommended - Free):")
    print("      - Visit https://huggingface.co/settings/tokens")
    print("      - Create a token and add to HUGGINGFACE_TOKEN in backend/.env")
    print("   b) Local Whisper (Free - runs on your machine):")
    print("      - No API key needed, just set SPEECH_API_TYPE=local_whisper")
    print("   c) Google Cloud (Free tier available):")
    print("      - Visit https://console.cloud.google.com/")
    print("      - Enable Speech-to-Text and Text-to-Speech APIs")
    print("      - Download credentials and set GOOGLE_CLOUD_CREDENTIALS path")
    print("   d) Azure Cognitive Services (Free tier available):")
    print("      - Visit https://portal.azure.com/")
    print("      - Create Speech resource and get key/region")
    print("      - Add AZURE_SPEECH_KEY and AZURE_SPEECH_REGION")
    print("   e) OpenAI (Paid):")
    print("      - Visit https://platform.openai.com/api-keys")
    print("      - Add your API key to OPENAI_API_KEY in backend/.env")
    print()
    print("3. Start the development servers:")
    print("   Backend:  cd backend && python -m uvicorn main:app --reload")
    print("   Frontend: cd frontend && npm start")
    print()
    print("4. Access the application:")
    print("   - Frontend: http://localhost:3000")
    print("   - Backend API: http://localhost:8000")
    print("   - API Docs: http://localhost:8000/docs")
    print()
    print("📚 For more information, check the README.md file")
    print("=" * 60)

def main():
    """Main setup function"""
    print_banner()
    
    # Check requirements
    check_python_version()
    if not check_node_version():
        print("\n❌ Please install Node.js from https://nodejs.org/")
        sys.exit(1)
    
    # Install dependencies
    if not install_backend_dependencies():
        sys.exit(1)
    
    if not install_frontend_dependencies():
        sys.exit(1)
    
    # Create environment files
    if not create_env_files():
        sys.exit(1)
    
    # Create directories
    if not create_directories():
        sys.exit(1)
    
    # Print next steps
    print_next_steps()

if __name__ == "__main__":
    main()
