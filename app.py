#!/usr/bin/env python3
"""
Main application entry point for single-tenant Azure Bot Service.
Compatible with Bot Framework SDK v4.17.0+
"""
import logging
import sys
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from aiohttp.web_request import BaseRequest
from botbuilder.core import (
    CloudAdapter,
    TurnContext,
    ConversationState,
    UserState,
    MemoryStorage
)
from botbuilder.core.integration import aiohttp_error_middleware
from botbuilder.schema import Activity
from config import Config
from bot import SingleTenantBot

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def create_app() -> web.Application:
    """Create and configure the aiohttp web application."""
    
    # Load and validate configuration
    config = Config()
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    # Create CloudAdapter with single-tenant authentication
    adapter = CloudAdapter(config.get_auth_config())
    
    # Create storage and state management
    memory_storage = MemoryStorage()
    conversation_state = ConversationState(memory_storage)
    user_state = UserState(memory_storage)
    
    # Create the bot instance
    bot = SingleTenantBot(conversation_state, user_state)
    
    # Configure error handler for the adapter
    async def on_error(context: TurnContext, error: Exception):
        """Handle adapter-level errors."""
        logger.error(f"Adapter error: {str(error)}")
        
        # Send error message to user
        from botbuilder.core import MessageFactory
        error_message = MessageFactory.text(
            "The bot encountered an error. Please try again later."
        )
        await context.send_activity(error_message)
        
        # Clear conversation state to prevent error loops
        await conversation_state.delete(context)
    
    adapter.on_turn_error = on_error
    
    # Define route handlers
    async def messages(req: Request) -> Response:
        """Handle incoming bot messages."""
        if "application/json" not in req.headers.get("Content-Type", ""):
            return Response(status=415, text="Content-Type must be application/json")
            
        try:
            body = await req.json()
        except Exception as e:
            logger.error(f"Error parsing JSON: {e}")
            return Response(status=400, text="Invalid JSON")
        
        activity = Activity().deserialize(body)
        auth_header = req.headers.get("Authorization", "")
        
        try:
            response = await adapter.process_activity(activity, auth_header, bot.on_turn)
            if response:
                return json_response(data=response.body, status=response.status)
            return Response(status=200)
        except Exception as e:
            logger.error(f"Error processing activity: {e}")
            return Response(status=500, text="Internal server error")
    
    async def health_check(req: Request) -> Response:
        """Health check endpoint for Azure monitoring."""
        return json_response({
            "status": "healthy",
            "app_type": config.MICROSOFT_APP_TYPE,
            "app_id": config.MICROSOFT_APP_ID[:8] + "..." if config.MICROSOFT_APP_ID else "not_set",
            "tenant_id": config.MICROSOFT_APP_TENANT_ID[:8] + "..." if config.MICROSOFT_APP_TENANT_ID else "not_set",
            "version": "1.0.0"
        })
    
    async def root(req: Request) -> Response:
        """Root endpoint with bot information."""
        return json_response({
            "message": "Single-Tenant Bot is running",
            "app_type": config.MICROSOFT_APP_TYPE,
            "sdk_version": "4.17.0+",
            "endpoints": {
                "messages": "/api/messages",
                "health": "/api/health"
            }
        })
    
    # Create web application with error middleware
    app = web.Application(middlewares=[aiohttp_error_middleware])
    
    # Add routes
    app.router.add_post("/api/messages", messages)
    app.router.add_get("/api/health", health_check)
    app.router.add_get("/", root)
    
    logger.info("Single-tenant bot application created successfully")
    return app


def main():
    """Main entry point for the application."""
    try:
        config = Config()
        app = create_app()
        
        # Run the application
        web.run_app(
            app, 
            host="0.0.0.0", 
            port=config.PORT
        )
    except Exception as e:
        logger.error(f"Failed to start application: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
