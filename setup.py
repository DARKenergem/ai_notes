#!/usr/bin/env python3
"""
Setup script for AI Notes Application
"""

import os
import sys
import subprocess
import base64
import secrets

def print_banner():
    print("=" * 60)
    print("🤖 AI-Powered Note-Taking Application Setup")
    print("=" * 60)

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 or higher is required")
        sys.exit(1)
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} detected")

def install_dependencies():
    """Install required dependencies"""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully")
    except subprocess.CalledProcessError:
        print("❌ Failed to install dependencies")
        sys.exit(1)

def generate_encryption_key():
    """Generate a secure encryption key"""
    key = secrets.token_bytes(32)
    return base64.b64encode(key).decode()

def create_env_file():
    """Create api.env file with configuration"""
    print("\n🔧 Creating environment configuration...")
    
    if os.path.exists("api.env"):
        print("⚠️  api.env file already exists. Skipping creation.")
        return
    
    # Get user input
    gemini_key = input("Enter your Gemini API key (or press Enter to skip): ").strip()
    mongo_uri = input("Enter MongoDB URI (default: mongodb://localhost:27017/): ").strip() or "mongodb://localhost:27017/"
    db_name = input("Enter database name (default: ai_notes): ").strip() or "ai_notes"
    
    # Generate encryption key
    encryption_key = generate_encryption_key()
    
    # Create api.env content
    env_content = f"""# Google Gemini AI Configuration
GEMINI_API_KEY={gemini_key}

# MongoDB Configuration
MONGO_URI={mongo_uri}
MONGO_DB_NAME={db_name}

# Encryption Configuration
NOTE_ENCRYPTION_KEY={encryption_key}

# FAISS Search Index Configuration
FAISS_INDEX_PATH=index.faiss
"""
    
    # Write api.env file
    with open("api.env", "w") as f:
        f.write(env_content)
    
    print("✅ api.env file created successfully")
    print(f"🔑 Generated encryption key: {encryption_key[:20]}...")

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    directories = ["calendar_events", "logs"]
    
    for directory in directories:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"✅ Created directory: {directory}")
        else:
            print(f"ℹ️  Directory already exists: {directory}")

def verify_setup():
    """Verify the setup"""
    print("\n🔍 Verifying setup...")
    
    # Check if api.env exists
    if not os.path.exists("api.env"):
        print("❌ api.env file not found")
        return False
    
    # Check if requirements are installed
    try:
        import typer
        import rich
        import pymongo
        import cryptography
        import google.generativeai
        print("✅ All required packages are available")
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        return False
    
    print("✅ Setup verification completed")
    return True

def main():
    print_banner()
    
    # Check Python version
    check_python_version()
    
    # Install dependencies
    install_dependencies()
    
    # Create directories
    create_directories()
    
    # Create .env file
    create_env_file()
    
    # Verify setup
    if verify_setup():
        print("\n🎉 Setup completed successfully!")
        print("\n📋 Next steps:")
        print("1. Start MongoDB: docker run -d -p 27017:27017 --name mongodb mongo:latest")
        print("2. Get a Gemini API key from: https://makersuite.google.com/app/apikey")
        print("3. Update your api.env file with the API key")
        print("4. Run: python -m modules.cli --help")
    else:
        print("\n❌ Setup verification failed. Please check the errors above.")

if __name__ == "__main__":
    main() 