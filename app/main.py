# # app/main.py
# # Minimal FastAPI + Bot Framework adapter entrypoint
# import os
# import sys
# import traceback
# from fastapi import FastAPI, Request, Response
# from fastapi.middleware.cors import CORSMiddleware
# from starlette.responses import JSONResponse
# from botbuilder.schema import Activity
# from botbuilder.integration.aiohttp import (
#     CloudAdapter,
#     ConfigurationBotFrameworkAuthentication,
# )
# from .config import DefaultConfig
# from .bots.echo_bot import EchoBot

# CONFIG = DefaultConfig()  # reads from env

# # Create adapter using configuration-based authentication (CloudAdapter)
# BOT_AUTH = ConfigurationBotFrameworkAuthentication(CONFIG)
# ADAPTER = CloudAdapter(BOT_AUTH)

# # Create your bot logic object
# BOT = EchoBot()

# # Generic on_turn_error handler
# async def on_error(context, error: Exception):
#     print(f"\n[on_turn_error] unhandled error: {error}", file=sys.stderr)
#     traceback.print_exc()
#     try:
#         # send friendly message to user
#         await context.send_activity("Sorry — something went wrong. The bot hit an error.")
#         # emit a trace activity when in emulator
#         if context.activity.channel_id == "emulator":
#             from botbuilder.schema import ActivityTypes, Activity as TraceActivity
#             trace = Activity(
#                 label="OnTurnError Trace",
#                 name="on_turn_error",
#                 timestamp=None,
#                 type=ActivityTypes.trace,
#                 value=str(error),
#                 value_type="https://www.botframework.com/schemas/error",
#             )
#             await context.send_activity(trace)
#     except Exception:
#         pass

# ADAPTER.on_turn_error = on_error

# app = FastAPI(title="FastAPI BotFramework Sample")

# # Optional CORS for local debugging / custom web chat
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # tighten in production
#     allow_methods=["*"],
#     allow_headers=["*"],
# )


# @app.post("/api/messages")
# async def messages(req: Request):
#     """
#     Bot Framework will POST activities here.
#     The SDK's CloudAdapter.process_activity handles auth and routes to bot.
#     """
#     body = await req.json()
#     auth_header = req.headers.get("Authorization", "")
#     activity = Activity().deserialize(body)
#     # process the activity through adapter -> calls bot.on_turn
#     invoke_response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)
#     # If there's an invoke response, return it to the caller (some activities return bodies)
#     if invoke_response:
#         return JSONResponse(status_code=invoke_response.status, content=invoke_response.body)
#     return Response(status_code=201)


# if __name__ == "__main__":
#     # for local debug only (run: python -m app.main)
#     import uvicorn

#     port = int(os.getenv("PORT", "3978"))
#     uvicorn.run("app.main:app", host="0.0.0.0", port=port, reload=True)


from fastapi import FastAPI, Request
from botbuilder.schema import Activity
from botbuilder.core import CloudAdapter, TurnContext

from app.bots.echo_bot import EchoBot
from app.config import DefaultConfig

CONFIG = DefaultConfig()
ADAPTER = CloudAdapter(CONFIG)
BOT = EchoBot()

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello! This is a FastAPI + Bot Framework echo bot."}

@app.post("/api/messages")
async def messages(request: Request):
    # 1️⃣ Get auth header
    auth_header = request.headers.get("Authorization", "")

    # 2️⃣ Parse request body into Activity object
    body = await request.json()
    activity = Activity().deserialize(body)

    # 3️⃣ Pass Activity object into adapter
    invoke_response = await ADAPTER.process_activity(activity, auth_header, BOT.on_turn)

    # 4️⃣ Return 200/InvokeResponse
    if invoke_response:
        return invoke_response.body
    return {"status": "OK"}