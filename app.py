import os
import sys
import logging
from aiohttp import web
from aiohttp.web import Request, Response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.integration.aiohttp import BotFrameworkHttpAdapter, aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes

# Configure logging for Azure App Service
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.StreamHandler(sys.stderr)
    ]
)

logger = logging.getLogger(__name__)

class EchoBot:
    """Simple echo bot that repeats user messages"""
    
    async def on_message_activity(self, turn_context: TurnContext):
        """Handle message activities"""
        user_message = turn_context.activity.text
        logger.info(f"Received message: {user_message}")
        
        # Echo the message back
        response_text = f"You said: {user_message}"
        await turn_context.send_activity(response_text)
        logger.info(f"Sent response: {response_text}")

    async def on_turn(self, turn_context: TurnContext):
        """Handle different types of activities"""
        logger.info(f"Processing activity type: {turn_context.activity.type}")
        
        if turn_context.activity.type == ActivityTypes.message:
            await self.on_message_activity(turn_context)
        elif turn_context.activity.type == ActivityTypes.members_added:
            await self._handle_members_added(turn_context)
        else:
            logger.info(f"Unhandled activity type: {turn_context.activity.type}")

    async def _handle_members_added(self, turn_context: TurnContext):
        """Welcome new members"""
        for member in turn_context.activity.members_added:
            if member.id != turn_context.activity.recipient.id:
                welcome_text = "Hello! I'm an echo bot. Send me a message and I'll echo it back!"
                await turn_context.send_activity(welcome_text)
                logger.info("Sent welcome message")

# Bot Framework Adapter settings
APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

logger.info(f"App ID configured: {'Yes' if APP_ID else 'No (empty)'}")
logger.info(f"App Password configured: {'Yes' if APP_PASSWORD else 'No (empty)'}")

# Create adapter
SETTINGS = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
ADAPTER = BotFrameworkHttpAdapter(SETTINGS)

# Error handler
async def on_error(context: TurnContext, error: Exception):
    """Error handler for the adapter"""
    logger.error(f"Bot encountered an error: {error}", exc_info=True)
    await context.send_activity("Sorry, it looks like something went wrong.")

ADAPTER.on_turn_error = on_error

# Create the bot instance
BOT = EchoBot()

# Health check endpoint
async def health_check(request: Request) -> Response:
    """Health check endpoint"""
    logger.info("Health check requested")
    return web.Response(text="Echo Bot is running!", status=200)

# Main messages endpoint
async def messages(req: Request) -> Response:
    """Main incoming endpoint for Bot Framework activities"""
    logger.info(f"Received {req.method} request to {req.path}")
    logger.info(f"Content-Type: {req.headers.get('Content-Type', 'None')}")
    logger.info(f"Headers: {dict(req.headers)}")
    
    # Check content type
    if "application/json" not in req.headers.get("Content-Type", ""):
        logger.error("Request is not application/json")
        return web.Response(status=406, text="Content-Type must be application/json")

    try:
        # Parse request body
        body = await req.json()
        logger.info(f"Received activity: {body.get('type', 'unknown')}")
        logger.debug(f"Activity body: {body}")
    except Exception as e:
        logger.error(f"Failed to parse request body: {e}")
        return web.Response(status=400, text="Invalid JSON")

    # Process the activity
    try:
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        
        # Process activity with adapter
        response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        
        if response:
            logger.info(f"Sending response with status {response.status}")
            return web.json_response(data=response.body, status=response.status)
        
        logger.info("Activity processed successfully, returning 202")
        return web.Response(status=202)
        
    except Exception as e:
        logger.error(f"Error processing activity: {e}", exc_info=True)
        return web.Response(status=500, text="Internal server error")

# Create the aiohttp application
app = web.Application(middlewares=[aiohttp_error_middleware])
app.router.add_post("/api/messages", messages)
app.router.add_get("/", health_check)
app.router.add_get("/health", health_check)

# Log startup
logger.info("Echo Bot application initialized")

# For local development
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    logger.info(f"Starting web server on port {port}")
    web.run_app(app, host="0.0.0.0", port=port)