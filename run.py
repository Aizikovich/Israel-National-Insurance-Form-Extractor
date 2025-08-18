#!/usr/bin/env python3
"""
Simple script to run the National Insurance Form Extractor application
"""

import os
import sys
import subprocess
from pathlib import Path


def check_requirements():
    """Check if all requirements are installed"""
    try:
        import streamlit
        import azure.ai.documentintelligence
        import openai
        import dotenv
        import PIL
        print("✅ All required packages are installed")
        return True
    except ImportError as e:
        print(f"Missing required package: {e}")
        print("Please run: pip install -r requirements.txt")
        return False


def check_env_file():
    """Check if .env file exists"""
    env_path = Path(".env")
    if not env_path.exists():
        print(" .env file not found")
        print("Please copy .env.example to .env and configure your Azure credentials")
        return False

    print("✅ .env file found")
    return True


def main():
    """Main function to run the application"""
    print("🚀 Starting National Insurance Form Extractor...")
    print("=" * 50)

    # Check requirements
    if not check_requirements():
        sys.exit(1)

    # Check environment file
    if not check_env_file():
        sys.exit(1)

    # Run the Streamlit application
    print(" Starting Streamlit application...")
    print(" The application will open in your browser at: http://localhost:8501")
    print(" Press Ctrl+C to stop the application")
    print("=" * 50)

    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "app.py",
            "--server.port", "8501",
            "--server.headless", "false"
        ])
    except KeyboardInterrupt:
        print("\n Application stopped by user")
    except Exception as e:
        print(f" Error running application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()