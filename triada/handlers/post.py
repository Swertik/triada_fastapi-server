# from sqlalchemy import text
#
# from triada.api.db_api import get_sessionmaker
# from triada.utils.patterns import BATTLE_PLAYERS_PATTERN, BATTLE_TIME_PATTERN
# from triada.config.settings import JUDGE_CHAT_ID
# from triada.schemas.models import Users
#
def handle_post():
    pass
# def handle_post(wall_object):
#     """
#     Обработчик постов
#     """
#     wall_object = wall_object.object
#
#     if players := BATTLE_PLAYERS_PATTERN.findall(wall_object['text']):
#         date = BATTLE_TIME_PATTERN.search(wall_object['text'])[1]
#         post_id = wall_object['id']
#         players = [{'user_id': i[0], 'user_name': i[1], 'character': i[2], 'universe': i[3]} for i in players]
#         engine = get_sessionmaker()
#         with engine.connect() as connection:
#             query = text('SELECT process_battle_transaction(:players, :post_id, :date)')
#             connection.exec(text, {'players': players, 'post_id': post_id, 'date': date})
#             new_players = [connection.add(Users(**i)) for i in players]
#             # cursor.executemany('INSERT INTO users(user_id, user_name) VALUES (?, ?) ON CONFLICT DO NOTHING',
#             #                    [(x[0], x[1]) for x in players])
#             # connection.commit()
#             # cursor.execute(f'Select judje_id from battles where link = {post_id}')
#             # judje_id = cursor.fetchone()[0]
#             # send_message(peer_id=JUDGE_CHAT_ID, message=f'Пост под судейством @{judje_id}(этого судьи)')



