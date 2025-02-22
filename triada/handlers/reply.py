from triada.config.settings import GROUP_ID
from triada.api.vk_api import send_message


async def handle_reply(reply: dict):
    if reply["from_id"] == GROUP_ID:
        return
    if reply["text"] == "test":
        await send_message(reply["peer_id"], "test")


