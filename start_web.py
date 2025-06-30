#!/usr/bin/env python3
"""
Startup script for Student Assistant Web Interface
"""

import sys
import os
from memory import get_message_count

def check_dependencies():
    try:
        import flask
        import ollama
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False

def main():
    print("🧠 Student Assistant - Web Interface")
    print("=" * 50)
    
    if not check_dependencies():
        print("Please run: pip install flask")
        sys.exit(1)
    
    print("🚀 Starting Web Interface...")
    print("📱 Open your browser to: http://localhost:5000")
    print("🧠 Memory status:", get_message_count(), "messages stored")
    print("🛑 Press Ctrl+C to stop")
    print()
    
    try:
        from app import app
        app.run(debug=False, host='0.0.0.0', port=5000)
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped")

if __name__ == "__main__":
    main()
