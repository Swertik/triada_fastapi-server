# import pytest
# from unittest.mock import AsyncMock, patch
# from triada.handlers.reply import handle_reply
# from fastapi.responses import PlainTextResponse
# import asyncio
# import httpx


# @pytest.mark.asyncio
# async def reply_test(reply: dict, called: bool = True):
#     # Создаем мок для httpx.AsyncClient
#     mock_response = AsyncMock()
#     mock_response.json.return_value = {"response": 1234567}  # Имитируем ответ от ВК

#     mock_client = AsyncMock()
#     mock_client.__aenter__.return_value.post.return_value = mock_response

#     with patch('httpx.AsyncClient', return_value=mock_client):
#         response = await handle_reply(reply)

#     if called:
#         mock_client.__aenter__.return_value.post.assert_called()
#         call_args = mock_client.__aenter__.return_value.post.call_args
#         assert call_args[0][0] == "https://api.vk.com/method/messages.send"
#         return response
#     else:
#         mock_client.__aenter__.return_value.post.assert_not_called()
#         return response



# if __name__ == "__main__":
#     print(asyncio.run(reply_test({'text': 'test', 
#                               'peer_id': 123456,
#                               'from_id': 123456}, called=True)))

