from sqlmodel import select

from triada.api.db_api import get_sessionmaker
from triada.api.vk_api import delete_comment
# from triada.api.vk_api import *
from triada.config.settings import GROUP_ID
from triada.schemas.models import Comment
from triada.schemas.table_models import BattlesPlayers


async def handle_reply(reply_object):
    """
    Обработчик ответов под постом
    """
    reply_object = Comment(**reply_object)
    if reply_object.from_id == -GROUP_ID:
        return

    async with get_sessionmaker()() as session:
        players = (await session.exec(select(BattlesPlayers.id).where(BattlesPlayers.link == reply_object.post_id))).all()
        if reply_object.from_id in players:
            if reply_object.reply_to_user is None:
                return 1
                #TODO: Обновление времени
            return 2
        else:
            await delete_comment(reply_object.id)
            return
            #TODO: Удаление коммента