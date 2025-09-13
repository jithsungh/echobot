# app.py
import os
import sys
import logging
from dotenv import load_dotenv
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.schema import Activity, ActivityTypes

from bot import EchoBot

# Load environment variables from .env file if it exists
load_dotenv()

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Log startup information
logging.info("Starting Echo Bot application")

# Bot Framework Adapter settings
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

logging.info(f"App ID configured: {'Yes' if APP_ID else 'No (empty)'}")
logging.info(f"App Password configured: {'Yes' if APP_PASSWORD else 'No (empty)'}")

SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Create the bot instance
BOT = EchoBot()

# Error handling middleware
async def error_middleware(request, handler):
    try:
        return await handler(request)
    except Exception as ex:
        logging.error(f"Error occurred: {ex}", exc_info=True)
        return web.Response(status=500, text="Internal server error")

# Main endpoint for incoming bot activities
async def messages(req: web.Request) -> web.Response:
    """
    Main incoming endpoint for Bot Framework activities.
    """
    logging.info(f"Received {req.method} request to {req.path}")
    logging.info(f"Content-Type: {req.headers.get('Content-Type', 'None')}")
    
    if "application/json" not in req.headers.get("Content-Type", ""):
        logging.error("Request is not of type application/json")
        return web.Response(status=406, text="Not Acceptable - Content-Type must be application/json")

    try:
        body = await req.json()
        logging.info("Received activity of type: %s", body.get("type"))
        logging.debug("Activity body: %s", body)
    except Exception as e:
        logging.error("Failed to parse request body: %s", e)
        return web.Response(status=400, text="Invalid JSON")

    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    try:
        response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        if response:
            logging.info("Sending response with status %s", response.status)
            return web.json_response(data=response.body, status=response.status)
        
        logging.info("Activity processed successfully, returning 202 Accepted")
        return web.Response(status=202)
    except Exception as exception:
        logging.error("Error processing activity: %s", exception, exc_info=True)
        return web.Response(status=500, text="Error processing activity")

# Create the aiohttp application
app = web.Application(middlewares=[error_middleware])
app.router.add_post("/api/messages", messages)
app.router.add_get("/", lambda request: web.Response(text="Echo Bot is running!"))

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    try:
        logging.info(f"Starting web server on host 0.0.0.0 and port {port}")
        web.run_app(app, host="0.0.0.0", port=port)
    except Exception as e:
        logging.error("Error starting web server: %s", e)
        raise