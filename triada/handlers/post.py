from sqlmodel import select, func
from triada.api.db_api import get_sessionmaker
from triada.api.vk_api import send_message
from triada.utils.patterns import BATTLE_PLAYERS_PATTERN, BATTLE_TIME_PATTERN
from triada.config.settings import JUDGE_CHAT_ID
from triada.schemas.table_models import Users, Battles
from triada.utils.db_commands import process_battle_transaction


async def handle_post(wall_object: dict) -> None:
    """
    Обработчик постов
    """
    if players := BATTLE_PLAYERS_PATTERN.findall(wall_object['text']):
        time_out = int(BATTLE_TIME_PATTERN.search(wall_object['text'])[1])
        post_id = wall_object['id']
        players = [{'user_id': int(i[0]), 'user_name': i[1], 'character': i[2], 'universe': i[3]} for i in players]
        async_engine = get_sessionmaker()
        async with async_engine() as connection:
            result = await process_battle_transaction(async_session=connection, player_data=players, battle_link=post_id, time_out_hours=time_out)
            await connection.commit()
            await connection.exec(select(Battles).where(Battles.link == post_id))
            await send_message(peer_id=JUDGE_CHAT_ID, text=f'Пост под судейством @id{result}(этого судьи)')
    return


