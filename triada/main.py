from triada.config.vk_types import  VkBotEventType
from triada.config.settings import CONFIRM_CODE
from triada.handlers.message import handle_message
from triada.handlers.post import handle_post
from triada.handlers.reply import handle_reply
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from triada.config.logg import logger
import httpx
from sqlmodel import Session, select
from triada.schemas.models import Battles, Users


def get_battle(session: Session, link: int = None, judge_id: int = None, status: str = None):
    if isinstance(link, int):
        print(link)
        return session.get(Battles, link)
    if isinstance(judge_id, int):
        return session.exec(select(Battles).where(Battles.judge_id == judge_id)).all()
    elif isinstance(status, str):
        return session.exec(select(Battles).where(Battles.status == status)).all()
    else:
        return session.exec(select(Battles)).all()


def get_user(session: Session, user_id: int):
    return session.get(Users, user_id)


app = FastAPI()


@app.get("/")
async def root():
    return PlainTextResponse("Hello World!")

@app.post("/new_confirm_code")
def new_confirm_code(confirm_code: str):
    global CONFIRM_CODE
    CONFIRM_CODE = confirm_code


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