import datetime

import pytest
from unittest.mock import patch, call, ANY
from datetime import timedelta
from triada.handlers.message import handle_message
from triada.config.settings import JUDGE_CHAT_ID, FLOOD_CHAT_ID
from triada.schemas.table_models import Battles, BattlesPlayers
from triada.tests.post_test import post_test


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
    async def test_hello(self, mock_vk_client):
        hello_calls = await message_test({'text': '.привет',
                                        'peer_id': JUDGE_CHAT_ID,
                                        'from_id': 123456}, called=True, mock_vk_client=mock_vk_client)
        assert hello_calls == [call('https://api.vk.com/method/messages.send', params={'access_token': ANY, 'peer_id': JUDGE_CHAT_ID, 'message': 'Привет!', 'random_id': ANY, 'v': '5.199', 'attachment': None})]

    @pytest.mark.asyncio
    async def test_call(self, mock_vk_client):
        vervict_calls = await message_test({'text': '.вердикт https://vk.com/wall-229144827_1 текст вердикта',
                                            'peer_id': JUDGE_CHAT_ID,
                                            'from_id': 123456}, called=True, mock_vk_client=mock_vk_client)
        assert vervict_calls == [call('https://api.vk.com/method/wall.createComment', params={'owner_id': -229144827, 'access_token': ANY, 'post_id': 1, 'message': 'текст вердикта', 'v': '5.199', 'attachment': None}), call('https://api.vk.com/method/messages.send', params={'access_token': ANY, 'peer_id': 2000000002, 'message': 'Комментарий в пост размещен!', 'random_id': ANY, 'v': '5.199', 'attachment': None})]


@pytest.mark.usefixtures('clear_db')
class TestMessageDB:
    @pytest.mark.asyncio
    async def test_pause(self, mock_vk_client, db_session):
                        # Не менять
        new_battle = Battles(link=1, judge_id=1, time_out=timedelta(hours=24))
        db_session.add(new_battle)
        await db_session.commit()
        pause_calls = await message_test(
            {'text': '.пауза https://vk.com/wall-229144827_1',
             'peer_id': JUDGE_CHAT_ID,
             'from_id': 123456},
            called=True,
            mock_vk_client=mock_vk_client
        )
        # Проверяем отправку сообщения
        assert pause_calls == [call('https://api.vk.com/method/wall.createComment', params={'owner_id': -229144827, 'access_token': ANY, 'post_id': 1, 'message': 'УВЕДОМЛЕНИЕ\n\nБой поставлен на паузу', 'v': '5.199', 'attachment': None}),
        call('https://api.vk.com/method/messages.send', params={'access_token': ANY, 'peer_id': 2000000002, 'message': 'Бой успешно поставлен на паузу!', 'random_id': ANY, 'v': '5.199', 'attachment': None})]

    @pytest.mark.asyncio
    async def test_my_battles(self, mock_vk_client, db_session):
        #TODO: Сделать link рандомным
        new_user_battle = BattlesPlayers(user_id=1, link=1000, time_out=datetime.datetime.now(), character='fff', universe='ff', user_name='Egor', turn=0)
        db_session.add(new_user_battle)
        await db_session.commit()
        my_battles_calls = await message_test({
            "text": '.мои бои',
            "peer_id": FLOOD_CHAT_ID,
            "from_id": 1
        }, called=True, mock_vk_client=mock_vk_client)

        assert my_battles_calls == [call('https://api.vk.com/method/messages.send', params={'access_token': ANY, 'peer_id': 2000000001, 'message': f'Ваши бои:\n\nhttps://vk.com/wall-229144827_1000', 'random_id': ANY, 'v': '5.199', 'attachment': None})]

