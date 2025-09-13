# app.py
import os
import sys
import logging
import asyncio
from dotenv import load_dotenv
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.integration.aiohttp import BotFrameworkHttpAdapter, aiohttp_error_middleware
from botbuilder.schema import Activity

from bot import EchoBot

# Configure logging to output to stdout
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)

# Load environment variables from .env file if it exists
load_dotenv()

# Bot Framework Adapter settings
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")
SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkHttpAdapter(SETTINGS)

# Create the bot instance
BOT = EchoBot()

# Main endpoint for incoming bot activities
async def messages(req: web.Request) -> web.Response:
    """
    Main incoming endpoint for Bot Framework activities.
    """
    if "application/json" not in req.headers.get("Content-Type", ""):
        logging.error("Request is not of type application/json")
        return web.Response(status=406)

    try:
        body = await req.json()
        logging.info("Received activity of type: %s", body.get("type"))
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
        
        logging.info("Activity processed, returning 202 Accepted")
        return web.Response(status=202)
    except Exception as exception:
        logging.error("Error processing activity: %s", exception, exc_info=True)
        raise exception

# Create the aiohttp application
app = web.Application(middlewares=[aiohttp_error_middleware])
app.router.add_post("/api/messages", messages)
app.router.add_get("/", lambda request: web.Response(text="Echo Bot is running."))

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    try:
        logging.info(f"Starting web server on host 0.0.0.0 and port {port}")
        # web.run_app(app, host="0.0.0.0", port=port)
    except Exception as e:
        logging.error("Error starting web server: %s", e)
        raise