#!/usr/bin/env python3
"""Script to run the chatbot in different modes"""

import argparse
import asyncio
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from main import main as run_console
from api.app import app


def run_api():
    """Run the API server"""
    import uvicorn
    from src.utils.config import Config
    
    config = Config()
    uvicorn.run(
        app,
        host=config.get("api.host", "localhost"),
        port=config.get("api.port", 8000),
        reload=config.get("api.debug", True)
    )


def main():
    """Main script entry point"""
    parser = argparse.ArgumentParser(description="Run Strands Agent Chatbot")
    parser.add_argument(
        "--mode",
        choices=["console", "api"],
        default="console",
        help="Run mode: console or api"
    )
    
    args = parser.parse_args()
    
    if args.mode == "console":
        asyncio.run(run_console())
    elif args.mode == "api":
        run_api()


if __name__ == "__main__":
    main()