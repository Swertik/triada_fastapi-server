from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from sqlmodel import select

from triada.schemas.table_models import Judges, Battles, BattlesPlayers


async def process_battle_transaction(
        async_session: AsyncSession,
        player_data: list[dict],  # Вместо JSONB передаем список словарей
        battle_link: int,
        time_out_hours: int
):
    users_ids = []
    # 1. Добавляем игроков
    for index, player in enumerate(player_data):
        battle_player = BattlesPlayers(
            user_id=player['user_id'],
            user_name=player['user_name'],
            character=player['character'],
            universe=player['universe'],
            turn=index,
            link=battle_link
        )
        users_ids.append(battle_player.user_id)
        async_session.add(battle_player)

    # 2. Выбираем судью с минимальным активными битвами и он не игрок

    selected_judge: Judges = (await async_session.execute(
        select(Judges)
        .where(Judges.judge_id.not_in(users_ids))
        .order_by(Judges.active_battles))
                      ).scalars().first()

    if not selected_judge:
        raise ValueError("No available judges")

    # 2. Создаем запись в battles
    new_battle = Battles(
        link=battle_link,
        judge_id=selected_judge.judge_id,
        time_out=timedelta(hours=time_out_hours)  # Предполагаем что в модели используется Interval
    )
    async_session.add(new_battle)

    # 3. Обновляем тайм-аут для первого игрока
    first_player = ((await async_session.exec(
        select(BattlesPlayers)
        .filter_by(link=battle_link, turn=0)))
        .first())

    if first_player:
        first_player.time_out = datetime.now() + timedelta(hours=time_out_hours)

    # 4. Обновляем счетчик активных битв у судьи
    selected_judge.active_battles += 1

    # Коммитим все изменения
    await async_session.commit()
    return selected_judge.judge_id