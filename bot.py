from botbuilder.core import TurnContext, ActivityHandler
from botbuilder.schema import ActivityTypes
import logging

logger = logging.getLogger(__name__)

class EchoBot(ActivityHandler):
    """Simple echo bot"""
    
    async def on_message_activity(self, turn_context: TurnContext):
        """Handle message activities"""
        user_message = turn_context.activity.text
        logger.info(f"Received message: {user_message}")
        
        response_text = f"You said: {user_message}"
        await turn_context.send_activity(response_text)
        logger.info(f"Sent response: {response_text}")

    async def on_members_added_activity(self, members_added, turn_context: TurnContext):
        """Welcome new members"""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity("Hello! I'm an echo bot. Send me a message!")
                logger.info("Sent welcome message")