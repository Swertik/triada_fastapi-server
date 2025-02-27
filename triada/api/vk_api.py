from fastapi import FastAPI
from pydantic import BaseModel
import httpx
from triada.config.settings import GROUP_TOKEN, MY_TOKEN, GROUP_ID
import asyncio
from random import randint

app = FastAPI()

#TODO: Прописать логику для attachments, добавить структуры из API вк (например forward)
async def send_message(peer_id: int, text: str, attachments=None) -> dict:
    """
    Отправляет сообщение через группу ВК
    
    Args:
        peer_id: ID получателя
        text: текст сообщения
        attachments: список вложений
    
    Returns:
        json:
            peer_id: Идентификатор назначения.
            message_id: Идентификатор сообщения.
            conversation_message_id: Идентификатор сообщения в диалоге.
            error: Сообщение об ошибке, если сообщение не было доставлено получателю.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.vk.com/method/messages.send",
            params={
                "access_token": GROUP_TOKEN,  # Токен сообщества
                "peer_id": peer_id,
                "message": text,
                "random_id": randint(1, 1000000000),  # Уникальный идентификатор (можно использовать random.randint)
                "v": "5.199",     # Версия API (актуальная)
                "attachment": attachments
            }
        )
    return response.json()


#TODO: Описать структуру возвращаемых данных у функций
async def send_comment(post_id: int, text: str, attachments=None) -> dict:
    """
    Отправляет комментарий к посту
    
    Args:
        post_id: ID поста
        text: текст комментария
        attachments: Прикрепленные объекты к комментарию
    
    Returns:
        json: ответ от ВК
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.vk.com/method/wall.createComment",
            params={
                "owner_id": -GROUP_ID,
                "access_token": GROUP_TOKEN,
                "post_id": post_id,
                "message": text,
                "v": "5.199",
                "attachment": attachments
            }
        )
    return response.json()


async def get_upload_server(group_id, album_id: int) -> dict:
    """
    Получает URL для загрузки фотографий
    
    Args:
        group_id: ID группы
        album_id: ID альбома
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.vk.com/method/photos.getUploadServer",
            params={
                "access_token": MY_TOKEN,
                "group_id": group_id,
                "album_id": album_id,
                "v": "5.199"
            }
        )
    return response.json()


async def close_comments(post_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.vk.com/method/wall.closeComments",
            params={"owner_id": -GROUP_ID, "post_id": post_id, "v": "5.199"}
        )
    return response.json()


async def open_comments(post_id: int) -> dict:
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.vk.com/method/wall.openComments",
            params={"owner_id": -GROUP_ID, "post_id": post_id, "v": "5.199"}
        )
    return response.json()


async def upload_photo(upload_url: str, photo: str) -> dict:
    """
    Загружает фотографию на сервер
    
    Args:
        upload_url: URL для загрузки фотографий
        photo: полный путь к фотографии
    
    Returns:
        json: ответ от ВК
    """
    async with httpx.AsyncClient() as client:
        with open(photo, "rb") as f:
            response = await client.post(
                upload_url,
                files={
                    "file": ('test.jpeg', f, "image/jpeg")
                }
            )
    return response.json()


async def save_photo(server: str, photos_list: str, group_id: int, album_id: int, unique_hash: str) -> dict:
    """
    Сохраняет фотографию на сервер
    
    Args:
        server: сервер для загрузки фотографий
        photos_list: фотография
        unique_hash: хэш фотографии
        album_id: идентификатор альбома, куда должны быть загружены фотографии
        group_id: идентификатор группы, куда должна быть загружена фотография

    Returns:
        json: ответ от ВК
    """

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.vk.com/method/photos.save",
            params={
                "access_token": MY_TOKEN,
                "server": server,
                "photos_list": photos_list,
                "hash": unique_hash,
                "album_id": album_id,
                "group_id": group_id,
                "v": "5.199"
            }
        )
    return response.json()

class LoadPhotoModel(BaseModel):
    group_id: int
    album_id: int
    photo: str


async def load_photo(data: LoadPhotoModel) -> dict:
    upload_server = await get_upload_server(data.group_id, data.album_id)
    upload_url = upload_server["response"]["upload_url"]
    upload_photos = await upload_photo(upload_url, data.photo)
    saved_photo = await save_photo(**upload_photos)
    return saved_photo


@app.get("/opa")
async def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    asyncio.run(send_comment(1,'fff'))
    #import uvicorn
    #uvicorn.run("vk_api:app", host="26.208.140.30", port=8080, reload=True)