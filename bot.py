# bot.py
from botbuilder.core import ActivityHandler, TurnContext

class EchoBot(ActivityHandler):
    async def on_message_activity(self, turn_context: TurnContext):
        text = (turn_context.activity.text or "").strip()
        # ---- Replace next line with a call into your LangChain chain ----
        reply_text = f"You said: {text}"
        await turn_context.send_activity(reply_text)
