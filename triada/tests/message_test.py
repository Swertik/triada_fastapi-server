import pytest
import pytest_asyncio
from unittest.mock import AsyncMock, patch, call, ANY
from triada.handlers.message import handle_message
from triada.config.settings import JUDGE_CHAT_ID
from triada.api.db_api import get_sessionmaker
from triada.schemas.models import Battles


@pytest_asyncio.fixture
async def mock_vk_client():
    mock_response = AsyncMock()
    mock_response.json.return_value = {"response": 1234567}
    
    mock_client = AsyncMock()
    mock_client.return_value.__aenter__.return_value.post.return_value = mock_response
    
    return mock_client


@pytest.mark.asyncio
async def message_test(message: dict, called: bool = True, mock_vk_client = None):
    if not mock_vk_client:
        mock_response = AsyncMock()
        mock_response.json.return_value = {"response": 1234567}
        
        mock_vk_client = AsyncMock()
        mock_vk_client.__aenter__.return_value.post.return_value = mock_response

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


@pytest.mark.usefixtures('setup_test_db')
class TestMessageDB:
    @pytest.mark.asyncio
    async def test_pause(self, mock_vk_client, db_session):
        new_battle = Battles()
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

