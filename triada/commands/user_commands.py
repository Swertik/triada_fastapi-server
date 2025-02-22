# """
# Реализации команд для пользователей
# """
# from triada.api.vk_api import send_message
# from triada.api.db_api import engine
# from .base import BaseCommand

# class HiddenActionCommand(BaseCommand):
#     """Команда для обработки скрытых действий"""

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

#         if not cursor.fetchall():
#             raise ValueError("Время для скрытого действия истекло")

#         cursor.execute(
#             "UPDATE battles_players SET hidden_action = %s WHERE link = %s AND user_id = %s",
#             (self.text, self.link, self.peer_id)
#         )

#     def _needs_commit(self) -> bool:
#         return True

#     def _send_success_message(self) -> None:
#         send_message(self.peer_id, "Скрытое действие записано") 