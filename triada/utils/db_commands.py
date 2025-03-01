from datetime import datetime, timedelta

from sqlmodel import select

from triada.api.db_api import get_sessionmaker
from triada.schemas.table_models import Judges, Battles, BattlesPlayers
from triada.utils.patterns import BATTLE_PLAYERS_PATTERN, BATTLE_TIME_PATTERN


async def process_battle_transaction(  # Вместо JSONB передаем список словарей
        post_id: int,
        text: str
):
    players = BATTLE_PLAYERS_PATTERN.findall(text)
    time_out_hours = int(BATTLE_TIME_PATTERN.search(text)[1])
    player_data = [{'user_id': int(i[0]), 'user_name': i[1], 'character': i[2], 'universe': i[3]} for i in players]
    async_engine = get_sessionmaker()
    async with async_engine() as async_session:
        # 1. Определяем id игроков
        users_ids = [int(i[0]) for i in players]


        # 2. Выбираем судью с минимальным активными битвами и он не игрок

        selected_judge: Judges = (await async_session.exec(
            select(Judges)
            .where(Judges.judge_id.not_in(users_ids))
            .order_by(Judges.active_battles))
                          ).first()

        if not selected_judge:
            raise ValueError("No available judges")

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
                user_id=player['user_id'],
                user_name=player['user_name'],
                character=player['character'],
                universe=player['universe'],
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

        # Коммитим все изменения
        await async_session.commit()
        return selected_judge.judge_id