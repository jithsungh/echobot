# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import sys
import traceback
import logging
from datetime import datetime

from aiohttp import web
from aiohttp.web import Request, Response, json_response
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
    BotFrameworkAdapter,
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity, ActivityTypes
from botbuilder.integration.aiohttp import CloudAdapter, ConfigurationBotFrameworkAuthentication

from bots import EchoBot
from config import DefaultConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONFIG = DefaultConfig()

# Create adapter with proper authentication for single tenant
# For single tenant bots, use CloudAdapter with proper authentication
auth_config = ConfigurationBotFrameworkAuthentication(
    app_id=CONFIG.APP_ID,
    app_password=CONFIG.APP_PASSWORD,
    app_type=CONFIG.APP_TYPE,
    app_tenant_id=CONFIG.APP_TENANT_ID
)

ADAPTER = CloudAdapter(auth_config)


# Catch-all for errors.
async def on_error(context: TurnContext, error: Exception):
    # This check writes out errors to console log .vs. app insights.
    # NOTE: In production environment, you should consider logging this to Azure
    #       application insights.
    logger.error(f"[on_turn_error] unhandled error: {error}")
    traceback.print_exc()

    # Send a message to the user
    await context.send_activity("The bot encountered an error or bug.")
    await context.send_activity(
        "To continue to run this bot, please fix the bot source code."
    )
    # Send a trace activity if we're talking to the Bot Framework Emulator
    if context.activity.channel_id == "emulator":
        # Create a trace activity that contains the error object
        trace_activity = Activity(
            label="TurnError",
            name="on_turn_error Trace",
            timestamp=datetime.utcnow(),
            type=ActivityTypes.trace,
            value=f"{error}",
            value_type="https://www.botframework.com/schemas/error",
        )
        # Send a trace activity, which will be displayed in Bot Framework Emulator
        await context.send_activity(trace_activity)


ADAPTER.on_turn_error = on_error

# Create the Bot
BOT = EchoBot()


# Listen for incoming requests on /api/messages
async def messages(req: Request) -> Response:
    """Main bot message handler."""
    try:
        # Validate content type
        content_type = req.headers.get("Content-Type", "")
        if "application/json" not in content_type:
            logger.warning(f"Invalid content type: {content_type}")
            return Response(status=415, text="Unsupported Media Type")

        # Parse request body
        body = await req.json()
        logger.info(f"Received activity: {body.get('type', 'unknown')}")

        # Create activity from request
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")

        # Process the activity
        response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
        
        if response:
            return json_response(data=response.body, status=response.status)
        return Response(status=200)
        
    except ValueError as ve:
        logger.error(f"Invalid JSON in request: {ve}")
        return Response(status=400, text="Invalid JSON")
    except Exception as e:
        logger.error(f"Error processing activity: {e}")
        traceback.print_exc()
        return Response(status=500, text="Internal Server Error")


# Health check endpoint
async def health_check(req: Request) -> Response:
    """Health check endpoint for Azure App Service."""
    return json_response({"status": "healthy", "timestamp": datetime.utcnow().isoformat()})


# Create application
APP = web.Application(middlewares=[aiohttp_error_middleware])
APP.router.add_post("/api/messages", messages)
APP.router.add_get("/health", health_check)
APP.router.add_get("/", health_check)  # Root endpoint for basic health check

if __name__ == "__main__":
    try:
        # In Azure App Service, the port is set by the platform
        # For local development, use the configured port
        host = "0.0.0.0"  # Listen on all interfaces for Azure App Service
        port = CONFIG.PORT
        
        logger.info(f"Starting bot server on {host}:{port}")
        logger.info(f"Bot configured for app type: {CONFIG.APP_TYPE}")
        logger.info(f"App ID: {CONFIG.APP_ID[:8]}..." if CONFIG.APP_ID else "No App ID configured")
        
        web.run_app(APP, host=host, port=port)
    except Exception as error:
        logger.error(f"Failed to start bot server: {error}")
        raise error
