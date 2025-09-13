# main.py
"""
Main entry point for Azure App Service deployment with aiohttp
This file ensures proper ASGI compatibility
"""
import logging
import sys
import os

# Configure logging for Azure
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)

# Import the aiohttp app
from app import app

# For Azure App Service - this is the WSGI application
application = app

if __name__ == "__main__":
    from aiohttp import web
    port = int(os.environ.get("PORT", 8000))
    logging.info(f"Starting Echo Bot on port {port}")
    web.run_app(app, host="0.0.0.0", port=port)
