"""
Single-tenant bot implementation with conversational capabilities.
Handles user interactions and maintains conversation state.
"""
import logging
from botbuilder.core import (
    ActivityHandler,
    TurnContext,
    MessageFactory,
    ConversationState,
    UserState,
    CardFactory
)
from botbuilder.schema import (
    Activity,
    ActivityTypes,
    ChannelAccount,
    SuggestedActions,
    CardAction,
    ActionTypes
)
import json
from datetime import datetime

logger = logging.getLogger(__name__)


class SingleTenantBot(ActivityHandler):
    """
    Single-tenant bot implementation with enhanced conversational capabilities.
    Maintains conversation and user state across interactions.
    """
    
    def __init__(self, conversation_state: ConversationState, user_state: UserState):
        """Initialize the bot with state management."""
        self.conversation_state = conversation_state
        self.user_state = user_state
        
        # Create state accessors
        self.conversation_data_accessor = self.conversation_state.create_property("ConversationData")
        self.user_profile_accessor = self.user_state.create_property("UserProfile")
        
        logger.info("SingleTenantBot initialized successfully")

    async def on_message_activity(self, turn_context: TurnContext):
        """Handle incoming message activities."""
        user_message = turn_context.activity.text.strip().lower()
        user_name = turn_context.activity.from_property.name or "User"
        
        logger.info(f"Received message from {user_name}: {turn_context.activity.text}")
        
        # Get conversation data
        conversation_data = await self.conversation_data_accessor.get(turn_context, lambda: {})
        user_profile = await self.user_profile_accessor.get(turn_context, lambda: {})
        
        # Update conversation data
        conversation_data["last_message"] = turn_context.activity.text
        conversation_data["message_count"] = conversation_data.get("message_count", 0) + 1
        conversation_data["last_activity"] = datetime.utcnow().isoformat()
        
        # Update user profile
        user_profile["name"] = user_name
        user_profile["last_seen"] = datetime.utcnow().isoformat()
        
        # Handle different message types
        response_text = await self._process_user_message(user_message, user_profile, conversation_data)
        
        # Create and send response
        response = MessageFactory.text(response_text)
        await turn_context.send_activity(response)
        
        # Save state changes
        await self.conversation_state.save_changes(turn_context)
        await self.user_state.save_changes(turn_context)

    async def _process_user_message(self, user_message: str, user_profile: dict, conversation_data: dict) -> str:
        """Process user message and generate appropriate response."""
        
        # Greeting handling
        if any(greeting in user_message for greeting in ["hello", "hi", "hey", "good morning", "good afternoon"]):
            user_name = user_profile.get("name", "there")
            return f"Hello {user_name}! How can I help you today? This is a secure single-tenant bot."
        
        # Help command
        elif user_message in ["help", "/help", "?", "what can you do"]:
            return self._get_help_message()
        
        # Status command
        elif user_message in ["status", "/status", "info"]:
            return self._get_status_message(user_profile, conversation_data)
        
        # Bot information
        elif "about" in user_message or "who are you" in user_message:
            return ("I'm a single-tenant bot built with Microsoft Bot Framework. "
                   "I'm designed to work securely within your Azure tenant and can help with various tasks.")
        
        # Default response with message count
        else:
            count = conversation_data.get("message_count", 1)
            return (f"You said: '{user_message}'\n\n"
                   f"This is message #{count} in our conversation. "
                   f"Type 'help' to see what I can do!")

    def _get_help_message(self) -> str:
        """Generate help message with available commands."""
        return """**Available Commands:**
        
• **hello/hi** - Greet the bot
• **help** - Show this help message  
• **status** - Show conversation statistics
• **about** - Learn about this bot

I'm a single-tenant bot running securely in your Azure environment. Feel free to chat with me about anything!"""

    def _get_status_message(self, user_profile: dict, conversation_data: dict) -> str:
        """Generate status message with conversation statistics."""
        message_count = conversation_data.get("message_count", 0)
        last_activity = conversation_data.get("last_activity", "Unknown")
        user_name = user_profile.get("name", "Unknown")
        
        return f"""**Conversation Status:**
        
• **User:** {user_name}
• **Messages in conversation:** {message_count}
• **Last activity:** {last_activity}
• **Bot type:** Single Tenant
• **Status:** Active and secure"""

    async def on_welcome_activity(self, turn_context: TurnContext):
        """Send welcome message to new users."""
        welcome_text = (
            "🤖 **Welcome to the Single-Tenant Bot!**\n\n"
            "I'm securely configured for single-tenant operation in Azure Bot Service. "
            "This means our conversations are private and isolated within your organization's tenant.\n\n"
            "Type **'help'** to see what I can do for you!"
        )
        
        # Create welcome message with suggested actions
        welcome_message = MessageFactory.text(welcome_text)
        welcome_message.suggested_actions = SuggestedActions(
            actions=[
                CardAction(
                    title="Help",
                    type=ActionTypes.im_back,
                    value="help"
                ),
                CardAction(
                    title="About",
                    type=ActionTypes.im_back,
                    value="about"
                ),
                CardAction(
                    title="Status",
                    type=ActionTypes.im_back,
                    value="status"
                )
            ]
        )
        
        await turn_context.send_activity(welcome_message)

    async def on_members_added_activity(
        self, members_added: list[ChannelAccount], turn_context: TurnContext
    ):
        """Handle new members being added to the conversation."""
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                await self.on_welcome_activity(turn_context)
                logger.info(f"New member added: {member.name}")

    async def on_error_activity(self, context: TurnContext, error: Exception):
        """Handle errors that occur during bot execution."""
        logger.error(f"Error in bot: {str(error)}", exc_info=True)
        
        error_message = MessageFactory.text(
            "🚨 Sorry, I encountered an error while processing your request. "
            "Please try again or contact support if the problem persists."
        )
        await context.send_activity(error_message)
        
        # Clear any corrupted state
        try:
            await self.conversation_state.clear_state(context)
        except Exception as clear_error:
            logger.error(f"Failed to clear state: {clear_error}")
