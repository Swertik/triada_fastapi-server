import datetime
import pytest

from unittest.mock import patch, call, ANY
from triada.handlers.reply import handle_reply



@pytest.mark.asyncio
async def reply_test(message: dict, called: bool = True, mock_vk_client = None):
    with patch('httpx.AsyncClient', return_value=mock_vk_client):
        response = await handle_reply(message)

    if called:
        mock_vk_client.__aenter__.return_value.post.assert_called()
        call_args = mock_vk_client.__aenter__.return_value.post.call_args_list
        return call_args
    else:
        mock_vk_client.__aenter__.return_value.post.assert_not_called()
        return response


class TestReply:
    @pytest.mark.asyncio
    async def test_valid_reply(self, mock_vk_client_factory):
        valid_reply_call = await reply_test({
            "text": "АААААААААААААААА БЛЯЯЯЯ",
            "post_id": 123,
            "from_id": 1,
            "date": datetime.datetime.now(),
            "id": 1
        }, called=False, mock_vk_client=mock_vk_client_factory())

        assert valid_reply_call == 1

    @pytest.mark.asyncio
    async def test_invalid_reply(self, mock_vk_client_factory):
        valid_reply_call = await reply_test({
            "text": "АААААААААААААААА БЛЯЯЯЯ",
            "post_id": 123,
            "from_id": 4,
            "date": datetime.datetime.now(),
            "id": 2
        }, called=True, mock_vk_client=mock_vk_client_factory())

        assert valid_reply_call == [call('https://api.vk.com/method/wall.deleteComment',
                                         params={'owner_id': -229144827,
                                                 'access_token': ANY,
                                                 'comment_id': 2,
                                                 'v': '5.199'})]
    @pytest.mark.asyncio
    async def test_polemic_reply(self, mock_vk_client_factory):
        polemic_reply_call = await reply_test({
            "text": "АААААААААААААААА БЛЯЯЯЯ",
            "post_id": 123,
            "from_id": 2,
            "date": datetime.datetime.now(),
            "id": 1,
            "reply_to_user": 1
        }, called=False, mock_vk_client=mock_vk_client_factory())

        assert polemic_reply_call == 2
