from triada.config.vk_types import  VkBotEventType
from triada.config.settings import CONFIRM_CODE
from triada.handlers.message import handle_message
from triada.handlers.post import handle_post
from triada.handlers.reply import handle_reply
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from triada.config.logg import logger

app = FastAPI()


@app.get("/")
async def root():
    return PlainTextResponse("Hello World!")


@app.post("/callback")
async def callback(data: dict):
    logger.info(data)
    if data["type"] == VkBotEventType.CONFIRMATION:
        return PlainTextResponse(CONFIRM_CODE)

    elif data["type"] == VkBotEventType.MESSAGE_NEW:
        await handle_message(data["object"]["message"])

    elif data["type"] == VkBotEventType.WALL_POST_NEW:
        pass
        await handle_post(data["object"])

    elif data["type"] == VkBotEventType.WALL_REPLY_NEW:
        pass
        await handle_reply(data["object"])

    return PlainTextResponse("ok")