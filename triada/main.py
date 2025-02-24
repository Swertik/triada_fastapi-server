from triada.config.vk_types import  VkBotEventType
from triada.config.settings import CONFIRM_CODE
from triada.handlers.message import handle_message
from triada.handlers.post import handle_post
from triada.handlers.reply import handle_reply
from fastapi import FastAPI
from fastapi.responses import PlainTextResponse
from triada.config.logg import logger
import httpx

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

if __name__ == "__main__":
     def send_confirm_code(confirm_code: str):
        """
        Отправляет сообщение через группу ВК

        Args:
            peer_id: ID получателя
            text: текст сообщения
            attachments: список вложений

        Returns:
            json: ответ от ВК
        """
        with httpx.Client() as client:
            response = client.post('https://buoyantly-endorsed-linnet.cloudpub.ru/new_confirm_code',
                                         params={"confirm_code": confirm_code})

        return response.json()

     send_confirm_code('6880bc81')