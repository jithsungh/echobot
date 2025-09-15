# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.

import logging
from botbuilder.core import ActivityHandler, MessageFactory, TurnContext
from botbuilder.schema import ChannelAccount, ActivityTypes

logger = logging.getLogger(__name__)


class EchoBot(ActivityHandler):
    """Echo bot implementation."""

    async def on_members_added_activity(
        self, members_added: list[ChannelAccount], turn_context: TurnContext
    ):
        """Greet new members when they join the conversation."""
        welcome_text = "Hello and welcome! I'm an echo bot. Send me a message and I'll echo it back to you."
        for member in members_added:
            if member.id != turn_context.activity.recipient.id:
                logger.info(f"New member added: {member.name}")
                await turn_context.send_activity(MessageFactory.text(welcome_text))

    async def on_message_activity(self, turn_context: TurnContext):
        """Echo back the user's message."""
        user_message = turn_context.activity.text
        logger.info(f"Received message: {user_message}")
        
        if user_message:
            echo_message = f"Echo: {user_message}"
            await turn_context.send_activity(MessageFactory.text(echo_message))
        else:
            await turn_context.send_activity(
                MessageFactory.text("I received a message, but it was empty. Please send me some text!")
            )

    async def on_turn(self, turn_context: TurnContext):
        """Handle all activity types."""
        logger.info(f"Activity type: {turn_context.activity.type}")
        await super().on_turn(turn_context)
