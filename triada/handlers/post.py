from triada.config.settings import GROUP_ID
from triada.api.vk_api import send_message


async def handle_post(post: dict):
    if post["from_id"] == GROUP_ID:
        return
    if post["text"] == "test":
        await send_message(post["peer_id"], "test")


