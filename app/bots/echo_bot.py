# app/bots/echo_bot.py
from botbuilder.core import ActivityHandler, TurnContext, MessageFactory
from botbuilder.schema import ChannelAccount


class EchoBot(ActivityHandler):
    async def on_members_added_activity(self, members_added: [ChannelAccount], turn_context: TurnContext):
        for member in members_added:
            # send welcome when user or bot is added (skip bot itself)
            if member.id != turn_context.activity.recipient.id:
                await turn_context.send_activity(
                    MessageFactory.text("Hello! I'm your FastAPI + Bot Framework echo bot. Say anything and I'll echo it.")
                )

    async def on_message_activity(self, turn_context: TurnContext):
        text = (turn_context.activity.text or "").strip()
        if not text:
            await turn_context.send_activity(MessageFactory.text("I didn't receive any text — try typing something."))
            return
        # echo back the user's message
        await turn_context.send_activity(MessageFactory.text(f"You said: {text}"))
