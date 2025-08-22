"""Script to run the Orchestrator Streamlit UI"""

import subprocess
import sys
import os

def main():
    """Run the Streamlit app for orchestrator"""
    # Get the path to the app
    app_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "agent_chatbot_orchestrator",
        "app_orchestrator.py"
    )
    
    # Run streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", app_path]
    
    print("🚀 Starting AWS Agent Orchestrator UI...")
    print(f"📁 App path: {app_path}")
    print("🌐 The app will open in your browser automatically")
    print("⏹️  Press Ctrl+C to stop the server")
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n👋 Stopping the server...")

if __name__ == "__main__":
    main()