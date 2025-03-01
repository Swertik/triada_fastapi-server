from sqlmodel import select, func
from triada.api.db_api import get_sessionmaker
from triada.api.vk_api import send_message
from triada.schemas.models import Post
from triada.utils.patterns import BATTLE_PLAYERS_PATTERN, BATTLE_TIME_PATTERN
from triada.config.settings import JUDGE_CHAT_ID
from triada.schemas.table_models import Users, Battles
from triada.utils.db_commands import process_battle_transaction


async def handle_post(wall_object: dict) -> None:
    """
    Обработчик постов
    """
    wall_object = Post(**wall_object)
    if BATTLE_PLAYERS_PATTERN.findall(wall_object.text):
            result = await process_battle_transaction(text=wall_object.text, post_id=wall_object.id)
            await send_message(peer_id=JUDGE_CHAT_ID, text=f'Пост под судейством @id{result}(этого судьи)')
    return


