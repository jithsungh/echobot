# app.py
import os
import sys
import logging
from dotenv import load_dotenv
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapter,
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.schema import Activity, ActivityTypes
from botbuilder.core.conversation_state import ConversationState
from botbuilder.core.memory_storage import MemoryStorage

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

# Create ConversationState using MemoryStorage
memory = MemoryStorage()
conversation_state = ConversationState(memory)

# Bot Framework Adapter settings
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

logging.info(f"App ID configured: {'Yes' if APP_ID else 'No (empty)'}")
logging.info(f"App Password configured: {'Yes' if APP_PASSWORD else 'No (empty)'}")

SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkAdapter(SETTINGS)

# Error handler for the adapter
async def on_error(context: TurnContext, error: Exception):
    """Error handler for the adapter"""
    logging.error(f"Bot encountered an error: {error}")
    logging.error("Traceback:", exc_info=True)
    
    # Send a message to the user
    await context.send_activity("Sorry, it looks like something went wrong.")

ADAPTER.on_turn_error = on_error

# Create the bot instance  
BOT = EchoBot(conversation_state)

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

# Health check endpoint
async def health_check(req: web.Request) -> web.Response:
    """Health check endpoint for Azure App Service"""
    return web.json_response({
        "status": "healthy",
        "app_id_configured": bool(APP_ID),
        "app_password_configured": bool(APP_PASSWORD)
    })

# Create the aiohttp application
app = web.Application(middlewares=[error_middleware])
app.router.add_post("/api/messages", messages)
app.router.add_get("/", lambda request: web.Response(text="Echo Bot is running!"))
app.router.add_get("/health", health_check)

# Main entry point
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    try:
        logging.info(f"Starting web server on host 0.0.0.0 and port {port}")
        web.run_app(app, host="0.0.0.0", port=port)
    except Exception as e:
        logging.error("Error starting web server: %s", e)
        raise