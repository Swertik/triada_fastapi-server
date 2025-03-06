from datetime import datetime, timedelta

from sqlalchemy.dialects.postgresql import insert
from sqlmodel import select
from triada.api.db_api import get_sessionmaker
from triada.api.vk_api import send_message
from triada.run.settings import JUDGE_CHAT_ID
from triada.schemas.table_models import Judges, Battles, BattlesPlayers, Users
from triada.utils.patterns import BATTLE_PLAYERS_PATTERN, BATTLE_TIME_PATTERN
from triada.schemas.models import BattleUsers

# async def process_add_users(users: List[dict]):
#     async_engine = get_sessionmaker()
#     async with async_engine() as async_session:
#         new_users = [Users(i['user_id'], i[]) for i in users]

async def process_battle_transaction(
        post_id: int,
        text: str
):
    players = BATTLE_PLAYERS_PATTERN.findall(text)
    time_out_hours = int(BATTLE_TIME_PATTERN.search(text)[1])
    users = [Users(user_id=int(i[0]), user_name=i[1]) for i in players]
    player_data = [BattleUsers(user_id=int(i[0]), user_name=i[1], character_name=i[2], universe_name= i[3]) for i in players]
    # 1. Определяем id игроков
    users_ids = [int(i[0]) for i in players]
    async with get_sessionmaker()() as async_session:
        # 2. Выбираем судью с минимальным активными битвами и он не игрок

        selected_judge: Judges = (await async_session.exec(
            select(Judges)
            .where(Judges.judge_id.not_in(users_ids))
            .order_by(Judges.active_battles))
                          ).first()

        if not selected_judge:
            raise ValueError(f"No available judges {(await async_session.exec(
            select(Judges))).all()}")

        # 2. Создаем запись в battles
        new_battle = Battles(
            link=post_id,
            judge_id=selected_judge.judge_id,
            time_out=timedelta(hours=time_out_hours)  # Предполагаем что в модели используется Interval
        )
        async_session.add(new_battle)

        # 3. Создаём записи игроков
        for index, player in enumerate(player_data):
            battle_player = BattlesPlayers(
                user_id=player.user_id,
                user_name=player.user_name,
                character=player.character_name,
                universe=player.universe_name,
                turn=index,
                link=post_id
            )
            async_session.add(battle_player)

        # 4. Обновляем тайм-аут для первого игрока
        first_player = ((await async_session.exec(
            select(BattlesPlayers)
            .filter_by(link=post_id, turn=0)))
            .first())

        if first_player:
            first_player.time_out = datetime.now() + timedelta(hours=time_out_hours)

        # 5. Обновляем счетчик активных битв у судьи
        selected_judge.active_battles += 1

        # 6. Добавляем всех пользователей
        stmt = insert(Users).values([user.model_dump() for user in users])
        stmt = stmt.on_conflict_do_nothing(index_elements=["user_id"])
        await async_session.execute(stmt)

        # Коммитим все изменения
        await async_session.commit()
        await send_message(peer_id=JUDGE_CHAT_ID, text=f'Пост под судейством @id{selected_judge.judge_id}(этого судьи)')
        return {"response": "ok"}


async def process_add_time(
    link: int,
    hours: timedelta
):
    async with get_sessionmaker()() as async_session:
        battle: BattlesPlayers = (await async_session.exec(select(BattlesPlayers).where(Battles.link == link))).first()
        battle.time_out += hours
        await async_session.commit()
    return {"response": "ok"}
