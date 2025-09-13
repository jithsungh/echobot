# bot.py
import logging
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory, ConversationState
from botbuilder.schema import ChannelAccount, ActivityTypes

class EchoBot(ActivityHandler):
    def __init__(self, conversation_state: ConversationState = None):
        """Initialize the bot with optional conversation state"""
        self.conversation_state = conversation_state

    async def on_message_activity(self, turn_context: TurnContext):
        """Handle message activities - this is where the bot responds to user messages"""
        try:
            user_text = turn_context.activity.text
            logging.info(f"Received message: {user_text}")
            
            if user_text:
                reply_text = f"Echo: {user_text}"
            else:
                reply_text = "I received your message, but it appears to be empty."
            
            # Send the reply
            await turn_context.send_activity(MessageFactory.text(reply_text))
            logging.info(f"Sent reply: {reply_text}")
            
            # Save conversation state if available
            if self.conversation_state:
                await self.conversation_state.save_changes(turn_context, False)
            
        except Exception as e:
            logging.error(f"Error in on_message_activity: {e}", exc_info=True)
            await turn_context.send_activity(MessageFactory.text("Sorry, I encountered an error processing your message."))

    async def on_members_added_activity(self, members_added: list[ChannelAccount], turn_context: TurnContext):
        """Handle members added events - send welcome message when users join"""
        try:
            for member in members_added:
                if member.id != turn_context.activity.recipient.id:
                    welcome_text = "Hello! I'm an Echo Bot. Send me a message and I'll echo it back to you."
                    await turn_context.send_activity(MessageFactory.text(welcome_text))
                    logging.info("Sent welcome message to new member")
                    
            # Save conversation state if available
            if self.conversation_state:
                await self.conversation_state.save_changes(turn_context, False)
                
        except Exception as e:
            logging.error(f"Error in on_members_added_activity: {e}", exc_info=True)

    async def on_turn(self, turn_context: TurnContext):
        """Called for every turn of the bot"""
        try:
            logging.info(f"Processing activity type: {turn_context.activity.type}")
            await super().on_turn(turn_context)
        except Exception as e:
            logging.error(f"Error in on_turn: {e}", exc_info=True)
            raise
