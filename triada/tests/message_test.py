import asyncio
from datetime import timedelta
import pytest
from unittest.mock import patch, call, ANY
from sqlalchemy import select
from triada.handlers.message import handle_message
from triada.config.settings import JUDGE_CHAT_ID, FLOOD_CHAT_ID
from triada.schemas.table_models import BattlesPlayers, Battles, Users


@pytest.mark.asyncio
async def message_test(message: dict, called: bool = True, mock_vk_client = None):
    with patch('httpx.AsyncClient', return_value=mock_vk_client):
        response = await handle_message(message)

    if called:
        mock_vk_client.__aenter__.return_value.post.assert_called()
        call_args = mock_vk_client.__aenter__.return_value.post.call_args_list
        return call_args
    else:
        mock_vk_client.__aenter__.return_value.post.assert_not_called()
        return response

class TestMessage:
    @pytest.mark.asyncio
    async def test_verdict(self, mock_vk_client_factory):
        verdict_calls = await message_test({'text': '.вердикт https://vk.com/wall-229144827_1 текст вердикта',
                                            'peer_id': JUDGE_CHAT_ID,
                                            'from_id': 123456}, called=True, mock_vk_client=mock_vk_client_factory())
        assert verdict_calls == [call('https://api.vk.com/method/wall.createComment', 
                                      params={'owner_id': -229144827, 
                                              'access_token': ANY, 
                                              'post_id': 1, 
                                              'message': 'текст вердикта', 
                                              'v': '5.199', 
                                              'attachment': None
                                              }),
                                call('https://api.vk.com/method/messages.send', 
                                     params={'access_token': ANY, 
                                             'peer_id': 2000000002, 
                                             'message': 'Комментарий в пост размещен!',
                                             'random_id': ANY, 
                                             'v': '5.199', 
                                             'attachment': None
                                             })]


    @pytest.mark.asyncio
    async def test_commands(self, mock_vk_client_factory):
        commands_calls = await message_test({
            "text": ".команды",
            "peer_id": FLOOD_CHAT_ID,
            "from_id": 1,
        }, called=True, mock_vk_client=mock_vk_client_factory())

        assert commands_calls == [call('https://api.vk.com/method/messages.send',
                                       params={'access_token': ANY,
                                               'peer_id': 1,
                                               'message': 'Команды:\n- мои бои\n- бои\n- команды',
                                               'random_id': ANY,
                                               'v': '5.199',
                                               'attachment': None
                                               })]



class TestMessageDB:

    @pytest.mark.asyncio
    async def test_my_battles(self, mock_vk_client_factory):
        my_battles_calls = await message_test({
            "text": '.мои бои',
            "peer_id": FLOOD_CHAT_ID,
            "from_id": 1
        }, called=True, mock_vk_client=mock_vk_client_factory())

        assert my_battles_calls == [call('https://api.vk.com/method/messages.send',
                                         params={'access_token': ANY,
                                                 'peer_id': 2000000001,
                                                 'message': f'Ваши бои:\n\nhttps://vk.com/wall-229144827_123',
                                                 'random_id': ANY,
                                                 'v': '5.199',
                                                 'attachment': None
                                                 })]

    @pytest.mark.asyncio
    async def test_battles(self, mock_vk_client_factory):
        battles_calls = await message_test({
            "text": ".бои",
            "peer_id": FLOOD_CHAT_ID,
            "from_id": 1
        }, called=True, mock_vk_client=mock_vk_client_factory())

        assert battles_calls == [call('https://api.vk.com/method/messages.send',
                                      params={'access_token': ANY,
                                              'peer_id': 2000000001,
                                              'message': 'Активные бои:\n\nhttps://vk.com/wall-229144827_123',
                                              'random_id': ANY,
                                              'v': '5.199',
                                              'attachment': None
                                              })]

    @pytest.mark.asyncio
    async def test_my_stat(self, mock_vk_client_factory):
        my_stat_calls = await message_test({
            "text": ".моя стата",
            "peer_id": FLOOD_CHAT_ID,
            "from_id": 1
        }, called=True, mock_vk_client=mock_vk_client_factory())

        assert my_stat_calls == [call('https://api.vk.com/method/messages.send',
                                      params={'access_token': ANY,
                                              'peer_id': 2000000001,
                                              'message': 'Ваша статистика:\n\nКоличество боев: 0\nКоличество побед: 0\nКоличество технических побед: 0\nКоличество поражений: 0\nКоличество технических поражений: 0\nВаш ММР: 100\nФрагменты побед: 0\nФрагменты величия: 0\nМесто в рейтинге: [В РАЗРАБОТКЕ]\n',
                                              'random_id': ANY,
                                              'v': '5.199',
                                              'attachment': None
                                              })]


    @pytest.mark.asyncio
    async def test_suspects(self, mock_vk_client_factory):
        suspects_calls = await message_test({
            "text": ".подсудимые",
            "peer_id": JUDGE_CHAT_ID,
            "from_id": 2
        }, called=True, mock_vk_client=mock_vk_client_factory())

        assert suspects_calls == [call('https://api.vk.com/method/messages.send', 
                                       params={'access_token': ANY, 
                                               'peer_id': 2000000002, 
                                               'message': 'Подсудимые:\n\nhttps://vk.com/wall-229144827_123', 
                                               'random_id': ANY, 
                                               'v': '5.199', 
                                               'attachment': None
                                               })]



    @pytest.mark.asyncio
    async def test_pause(self, mock_vk_client_factory, db_session):
        pause_calls = await message_test(
            {'text': '.пауза https://vk.com/wall-229144827_123',
             'peer_id': JUDGE_CHAT_ID,
             'from_id': 123456},
            called=True,
            mock_vk_client=mock_vk_client_factory()
        )
        # Проверяем отправку сообщения
        battle_status = (await db_session.exec(select(Battles).
                                                       where(Battles.link == 123))
                                 ).first()[0].status

        assert pause_calls == [call('https://api.vk.com/method/wall.createComment',
                                    params={'owner_id': -229144827,
                                            'access_token': ANY,
                                            'post_id': 123,
                                            'message': 'УВЕДОМЛЕНИЕ\n\nБой поставлен на паузу',
                                            'v': '5.199',
                                            'attachment': None
                                            }),
                               call('https://api.vk.com/method/messages.send',
                                    params={'access_token': ANY,
                                            'peer_id': 2000000002,
                                            'message': 'Бой успешно поставлен на паузу!',
                                            'random_id': ANY,
                                            'v': '5.199',
                                            'attachment': None
                                            })]
        assert battle_status == "paused"



    @pytest.mark.asyncio
    async def test_unpause(self, mock_vk_client_factory, db_session):
        unpause_calls = await message_test({
            "text": ".возобновить https://vk.com/wall-229144827_123",
            "peer_id": JUDGE_CHAT_ID,
            "from_id": 2
        }, called=True, mock_vk_client=mock_vk_client_factory())

        battle_status = (await db_session.exec(select(Battles).
                                               where(Battles.link == 123))
                         ).first()[0].status

        assert unpause_calls == [call('https://api.vk.com/method/wall.createComment', 
                                      params={'owner_id': -229144827, 
                                              'access_token': ANY, 
                                              'post_id': 123, 
                                              'message': 'УВЕДОМЛЕНИЕ\n\nБой снят с паузы', 
                                              'v': '5.199', 
                                              'attachment': None
                                              }),
                                      call('https://api.vk.com/method/messages.send', 
                                           params={'access_token': ANY, 
                                                   'peer_id': 2000000002, 
                                                   'message': 'Бой успешно снят с паузы!', 
                                                   'random_id': ANY, 
                                                   'v': '5.199', 
                                                   'attachment': None
                                                   })]
        assert battle_status == "active"


    @pytest.mark.asyncio
    async def test_close_battle(self, mock_vk_client_factory, db_session):
        close_battle_calls = await message_test({
            "text": ".закрыть https://vk.com/wall-229144827_123",
            "peer_id": JUDGE_CHAT_ID,
            "from_id": 2
        }, called=True, mock_vk_client=mock_vk_client_factory())

        battle_status = (await db_session.exec(select(Battles).
                                               where(Battles.link == 123))
                         ).first()[0].status

        assert close_battle_calls == [call('https://api.vk.com/method/wall.closeComments', 
                                           params={'owner_id': -229144827, 
                                                   'post_id': 123, 
                                                   'v': '5.199'
                                                   }),
                                      call('https://api.vk.com/method/wall.createComment', 
                                           params={'owner_id': -229144827, 
                                                   'access_token': ANY, 
                                                   'post_id': 123, 
                                                   'message': 'УВЕДОМЛЕНИЕ\n\nБой закрыт!', 
                                                   'v': '5.199', 
                                                   'attachment': None
                                                   }),
                                      call('https://api.vk.com/method/messages.send', 
                                           params={'access_token': ANY, 
                                                   'peer_id': 2000000002, 
                                                   'message': 'Бой успешно закрыт!', 
                                                   'random_id': ANY, 
                                                   'v': '5.199', 
                                                   'attachment': None
                                                   })]

        assert battle_status == "closed"


    @pytest.mark.asyncio
    async def test_extend(self, mock_vk_client_factory, db_session):
        battle_time_out_first = (await db_session.exec(select(BattlesPlayers.time_out).
                                                       where((BattlesPlayers.link == 123) & (BattlesPlayers.time_out.is_not(None))))
                                 ).first()[0]

        extend_calls = await message_test({
            "text": ".продление https://vk.com/wall-229144827_123 24",
            "peer_id": JUDGE_CHAT_ID,
            "from_id": 2
        }, called=True, mock_vk_client=mock_vk_client_factory())


        assert extend_calls == [call('https://api.vk.com/method/wall.createComment', 
                                      params={'owner_id': -229144827, 
                                              'access_token': ANY, 
                                              'post_id': 123, 
                                              'message': 'УВЕДОМЛЕНИЕ\n\nБой продлён на 24 часов.', 
                                              'v': '5.199', 
                                              'attachment': None
                                              }),
                                      call('https://api.vk.com/method/messages.send', 
                                           params={'access_token': ANY, 
                                                   'peer_id': 2000000002, 
                                                   'message': 'В бою успешно проведено продление!', 
                                                   'random_id': ANY, 
                                                   'v': '5.199', 
                                                   'attachment': None
                                                   })]
        battle_time_out_second = (await db_session.exec(select(BattlesPlayers.time_out).
                                                       where((BattlesPlayers.link == 123) & (BattlesPlayers.time_out.is_not(None))))
                                 ).first()[0]

        assert battle_time_out_first+timedelta(hours=24) == battle_time_out_second

    @pytest.mark.asyncio
    async def test_activation_grade(self, mock_vk_client_factory, db_session):
        grade_activation_calls = await message_test({
            "text": ".оценка https://vk.com/wall-229144827_123",
            "peer_id": JUDGE_CHAT_ID,
            "from_id": 2
        }, called=True, mock_vk_client=mock_vk_client_factory())


        assert grade_activation_calls == [call('https://api.vk.com/method/messages.send',
                                    params={'access_token': ANY,
                                            'peer_id': 2000000002,
                                            'message': 'Игроки:\n@id1(Egor)\n@id2(Asya)\n@id3(Kiz)',
                                            'random_id': ANY,
                                            'v': '5.199',
                                            'attachment': None
                                            })]

        grade_calls = await message_test({
            "text": "Победа: 51\nПоражение: -51\nПобеда: 51",
            "peer_id": JUDGE_CHAT_ID,
            "from_id": 2
        }, called=True, mock_vk_client=mock_vk_client_factory())

        assert grade_calls == [call('https://api.vk.com/method/messages.send',
                                    params={'access_token': ANY,
                                            'peer_id': 2000000002,
                                            'message': 'Оценка успешно добавлена!',
                                            'random_id': ANY,
                                            'v': '5.199',
                                            'attachment': None}),
                               call('https://api.vk.com/method/wall.closeComments',
                                    params={'owner_id': -229144827,
                                            'post_id': 123,
                                            'v': '5.199'})]

        result = (await db_session.exec(select(Users))).all()
        assert result == [(Users(user_id=1,
                                 technical_wins=0,
                                 technical_losses=0,
                                 fragments_of_victories=0,
                                 skill_rating=0,
                                 losses=0,
                                 user_name='Egor',
                                 wins=1,
                                 mmr=151,
                                 fragments_of_greatness=0),),
                          (Users(user_id=2,
                                 technical_wins=0,
                                 technical_losses=0,
                                 fragments_of_victories=0,
                                 skill_rating=0,
                                 losses=1,
                                 user_name='Asya',
                                 wins=0,
                                 mmr=49,
                                 fragments_of_greatness=0),),
                          (Users(user_id=3,
                                 technical_wins=0,
                                 technical_losses=0,
                                 fragments_of_victories=0,
                                 skill_rating=0,
                                 losses=0,
                                 user_name='Kiz',
                                 wins=1,
                                 mmr=151,
                                 fragments_of_greatness=0),)]
