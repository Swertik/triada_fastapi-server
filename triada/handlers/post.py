from triada.schemas.models import Post
from triada.utils.patterns import BATTLE_PLAYERS_PATTERN
from triada.utils.db_commands import process_battle_transaction


async def handle_post(wall_object: dict) -> None:
    """
    Обработчик постов
    """
    wall_object = Post(**wall_object)
    if BATTLE_PLAYERS_PATTERN.findall(wall_object.text):
        await process_battle_transaction(text=wall_object.text, post_id=wall_object.id)

    return


