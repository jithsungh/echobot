# app.py
import os
import asyncio
from aiohttp import web
from botbuilder.core import (
    BotFrameworkAdapterSettings,
    TurnContext,
)
from botbuilder.integration.aiohttp import BotFrameworkHttpAdapter, aiohttp_error_middleware
from botbuilder.schema import Activity

from bot import EchoBot  # simple handler below

APP_ID = os.environ.get("MicrosoftAppId", "")
APP_PASSWORD = os.environ.get("MicrosoftAppPassword", "")

settings = BotFrameworkAdapterSettings(APP_ID, APP_PASSWORD)
adapter = BotFrameworkHttpAdapter(settings)

BOT = EchoBot()

async def messages(req: web.Request) -> web.Response:
    """Main incoming endpoint for Bot Framework activities."""
    try:
        body = await req.json()
    except Exception:
        return web.Response(status=400, text="Invalid JSON")

    activity = Activity().deserialize(body)
    auth_header = req.headers.get("Authorization", "")

    # Process the activity using the adapter -> will call bot.on_turn
    async def call_bot(adapter_context):
        await BOT.on_turn(adapter_context)

    # process_activity returns a BotFrameworkResponse or None
    response = await adapter.process_activity(activity, auth_header, BOT.on_turn)
    # Many samples return 201 / 200. The adapter may return a response object.
    return web.Response(status=201)

app = web.Application(middlewares=[aiohttp_error_middleware])
app.router.add_post("/api/messages", messages)
app.router.add_get("/", lambda request: web.Response(text="Echo Bot is running."))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 3978))
    web.run_app(app, host="0.0.0.0", port=port)
