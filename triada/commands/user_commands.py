"""
Реализации команд для пользователей
"""
# from sqlmodel import Session, select
#
# from triada.api.vk_api import send_message
# from triada.api.db_api import get_session
# from triada.commands.base import BaseCommand, BaseDBCommand, BaseUserDBCommand
# from triada.schemas.models import BattlesPlayers



# class HiddenActionCommand(BaseCommand):
#     """Команда для обработки скрытых действий"""
#
#     def _execute_command(self) -> None:
#         cursor.execute("""
#             SELECT user_id
#             FROM battles_players bp
#             WHERE bp.link = %s
#             AND (
#                 (SELECT MAX(time_out) FROM battles_players WHERE link = %s) -
#                 (SELECT time_out FROM battles WHERE link = %s) +
#                 INTERVAL '1 hour'
#             ) > current_timestamp
#             AND bp.hidden_action = 'active'
#         """, (self.link, self.link, self.link))
#
#         if not cursor.fetchall():
#             raise ValueError("Время для скрытого действия истекло")
#
#         cursor.execute(
#             "UPDATE battles_players SET hidden_action = %s WHERE link = %s AND user_id = %s",
#             (self.text, self.link, self.peer_id)
#         )
#
#     def _needs_commit(self) -> bool:
#         return True
#
#     def _send_success_message(self) -> None:
#         send_message(self.peer_id, "Скрытое действие записано")

# class MyBattlesCommand(BaseUserDBCommand):
#     async def _execute_command(self, session: Session):
#         user_battles = (await session.exec(select(BattlesPlayers).where(BattlesPlayers.user_id == self.peer_id))).fetchall()
#         print(user_battles)
#
#     async def _send_success_message(self) -> None:
#         #TODO: Добавить нормальное сообщение
#         await send_message(self.peer_id, 'f')