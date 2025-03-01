import datetime

import pytest
from unittest.mock import patch, call, ANY
from datetime import timedelta

from sqlalchemy import delete
from sqlmodel import select

from triada.handlers.message import handle_message
from triada.config.settings import JUDGE_CHAT_ID, FLOOD_CHAT_ID
from triada.schemas.table_models import Battles, BattlesPlayers, Users
from triada.tests.conftest import test_db


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
    async def test_verdict(self, mock_vk_client):
        verdict_calls = await message_test({'text': '.вердикт https://vk.com/wall-229144827_1 текст вердикта',
                                            'peer_id': JUDGE_CHAT_ID,
                                            'from_id': 123456}, called=True, mock_vk_client=mock_vk_client)
        assert verdict_calls == [call('https://api.vk.com/method/wall.createComment', params={'owner_id': -229144827, 'access_token': ANY, 'post_id': 1, 'message': 'текст вердикта', 'v': '5.199', 'attachment': None}), call('https://api.vk.com/method/messages.send', params={'access_token': ANY, 'peer_id': 2000000002, 'message': 'Комментарий в пост размещен!', 'random_id': ANY, 'v': '5.199', 'attachment': None})]

    @pytest.mark.asyncio
    async def test_commands(self, mock_vk_client):
        commands_calls = await message_test({
            "text": ".команды",
            "peer_id": FLOOD_CHAT_ID,
            "from_id": 1,
        }, called=True, mock_vk_client=mock_vk_client)

        assert commands_calls == [call('https://api.vk.com/method/messages.send',
                                       params={'access_token': ANY,
                                               'peer_id': 1,
                                               'message': 'Команды:\n- мои бои\n- бои\n- команды',
                                               'random_id': ANY,
                                               'v': '5.199',
                                               'attachment': None})]

@pytest.mark.usefixtures('clear_db')
class TestMessageDB:

    @pytest.mark.asyncio
    async def test_pause(self, mock_vk_client, db_session, test_db):
        pause_calls = await message_test(
            {'text': '.пауза https://vk.com/wall-229144827_123',
             'peer_id': JUDGE_CHAT_ID,
             'from_id': 123456},
            called=True,
            mock_vk_client=mock_vk_client
        )
        # Проверяем отправку сообщения
        assert pause_calls == [call('https://api.vk.com/method/wall.createComment', params={'owner_id': -229144827, 'access_token': ANY, 'post_id': 123, 'message': 'УВЕДОМЛЕНИЕ\n\nБой поставлен на паузу', 'v': '5.199', 'attachment': None}),
        call('https://api.vk.com/method/messages.send', params={'access_token': ANY, 'peer_id': 2000000002, 'message': 'Бой успешно поставлен на паузу!', 'random_id': ANY, 'v': '5.199', 'attachment': None})]

    @pytest.mark.asyncio
    async def test_my_battles(self, mock_vk_client, db_session):
        #TODO: Сделать link рандомным
        my_battles_calls = await message_test({
            "text": '.мои бои',
            "peer_id": FLOOD_CHAT_ID,
            "from_id": 1
        }, called=True, mock_vk_client=mock_vk_client)

        assert my_battles_calls == [call('https://api.vk.com/method/messages.send',
                                         params={'access_token': ANY,
                                                 'peer_id': 2000000001,
                                                 'message': f'Ваши бои:\n\nhttps://vk.com/wall-229144827_123',
                                                 'random_id': ANY, 'v': '5.199', 'attachment': None})]

    @pytest.mark.asyncio
    async def test_battles(self, mock_vk_client, db_session):
        battles_calls = await message_test({
            "text": ".бои",
            "peer_id": FLOOD_CHAT_ID,
            "from_id": 1
        }, called=True, mock_vk_client=mock_vk_client)

        assert battles_calls == [call('https://api.vk.com/method/messages.send',
                                      params={'access_token': ANY,
                                              'peer_id': 2000000001,
                                              'message': 'Активные бои:\n\nhttps://vk.com/wall-229144827_123',
                                              'random_id': ANY,
                                              'v': '5.199',
                                              'attachment': None})]

    @pytest.mark.asyncio
    async def test_my_stat(self, mock_vk_client, db_session):
        my_stat_calls = await message_test({
            "text": ".моя стата",
            "peer_id": FLOOD_CHAT_ID,
            "from_id": 1
        }, called=True, mock_vk_client=mock_vk_client)

        assert my_stat_calls == [call('https://api.vk.com/method/messages.send',
                                      params={'access_token': ANY,
                                              'peer_id': 2000000001,
                                              'message': 'Ваша статистика:\n\nКоличество боев: 0\nКоличество побед: 0\nКоличество технических побед: 0\nКоличество поражений: 0\nКоличество технических поражений: 0\nВаш ММР: 100\nФрагменты побед: 0\nФрагменты величия: 0\nМесто в рейтинге: [В РАЗРАБОТКЕ]\n',
                                              'random_id': ANY,
                                              'v': '5.199',
                                              'attachment': None})]