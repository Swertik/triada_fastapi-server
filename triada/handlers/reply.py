from sqlmodel import select

from triada.api.db_api import get_sessionmaker
# from triada.api.vk_api import *
from triada.config.logg import logger
from triada.config.settings import GROUP_ID
from triada.schemas.models import Comment
from triada.schemas.table_models import BattlesPlayers


async def handle_reply(reply_object):
    pass
    # """
    # Обработчик ответов под постом
    # """
    # reply_object = Comment(**reply_object)
    # if reply_object.from_id == -GROUP_ID:
    #     return
    #
    # async_engine = get_sessionmaker()
    # async with async_engine() as connection:
    #     players = (await connection.exec(select(BattlesPlayers).where(BattlesPlayers.link == reply_object.post_id and BattlesPlayers.time_out is not None))).all()
    #     if reply_object.from_id in players:
    #         if reply_object['text'].lower().startswith('продление'):
    #             hours = abs(int(reply_object['text'].split(' ')[1]))
    #             cursor.execute(f'SELECT process_add_time({post_id},{hours})')
    #             connection.commit()
    #
    #         elif reply_object.get('reply_to_user') is None:
    #             cursor.execute(f'SELECT process_turn_update({post_id})')
    #             connection.commit()
    #
    #     else:
    #         logger.info('GGGGGG')
    #         vk_user.wall.deleteComment(owner_id=-GROUP_ID, comment_id=reply_object['id'])