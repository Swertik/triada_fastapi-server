from triada.config.vk_types import  VkBotEventType
from triada.handlers.message import handle_message
from triada.handlers.post import handle_post
from triada.handlers.reply import handle_reply
from fastapi import FastAPI, Depends
from fastapi.responses import PlainTextResponse
from triada.config.logg import logger
from triada.api.db_api import get_session

app = FastAPI()


@app.get("/")
async def root():
    return PlainTextResponse("Hello World!")

@app.post("/new_confirm_code")
def new_confirm_code(confirm_code: str):
    global CONFIRM_CODE
    CONFIRM_CODE = confirm_code


@app.post("/callback", dependencies=[Depends(get_session)])
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