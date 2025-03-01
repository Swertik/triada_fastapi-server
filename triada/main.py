import uvicorn
from sqlmodel import select

from triada.api.vk_api import get_post_by_id
from triada.config.settings import GROUP_ID
from triada.config.vk_types import  VkBotEventType
from triada.handlers.message import handle_message
from triada.handlers.post import handle_post
from triada.handlers.reply import handle_reply
from fastapi import FastAPI, Depends
from fastapi.responses import PlainTextResponse
from triada.config.logg import logger
from triada.api.db_api import get_session, get_sessionmaker
from triada.schemas.table_models import Battles, Judges
from triada.utils.db_commands import process_battle_transaction


CONFIRM_CODE = "c2edaf9e"


app = FastAPI()

@app.get("/")
async def root():
    return PlainTextResponse("Hello World!")

@app.post("/new_confirm_code")
def new_confirm_code(confirm_code: str):
    global CONFIRM_CODE
    CONFIRM_CODE = confirm_code


@app.post("/post_to_battles/{post_id}")
async def post_to_battles(post_id: int):
    post = await get_post_by_id(posts=[f'-{GROUP_ID}_{post_id}'])
    post_text = post["response"]['items'][0]['text']
    try:
        await process_battle_transaction(post_id, post_text)
        return {"response": "ok"}
    except Exception as e:
        logger.error(e)
        return {"response": "error", "error": str(e)}


@app.get("/judges")
async def get_judges():

    session = get_sessionmaker()
    async with session() as async_session:
        judges = (await async_session.exec(select(Judges))).all()
    return {"battles": judges}


@app.get("/battles")
async def get_battles():
    session = get_sessionmaker()
    async with session() as async_session:
        all_battles = (await async_session.exec(select(Battles).where(Battles.status != 'closed'))).all()
    return {"battles": all_battles}


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

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)