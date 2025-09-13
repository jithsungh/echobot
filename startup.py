# startup.py
"""
Startup script for Azure App Service deployment
This ensures proper ASGI/WSGI compatibility
"""
import logging
from app import app

# Configure logging for Azure
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# Export the app for Gunicorn
application = app

if __name__ == "__main__":
    import os
    from aiohttp import web
    
    port = int(os.environ.get("PORT", 3978))
    logging.info(f"Starting application on port {port}")
    web.run_app(app, host="0.0.0.0", port=port)
