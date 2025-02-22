# import pytest
# import pytest_asyncio
# from unittest.mock import AsyncMock, patch
# from triada.api.vk_api import send_message, send_comment
# from fastapi.responses import PlainTextResponse
# import asyncio
#
#
#
# @pytest_asyncio.fixture
# async def mock_vk_client():
#     mock_response = AsyncMock()
#     mock_response.json.return_value = {"response": 1234567}
#
#     mock_client = AsyncMock()
#     mock_client.__aenter__.return_value.post.return_value = mock_response
#
#     return mock_client
#
#
# @pytest.mark.asyncio
# async def test_send_message_to_vk(mock_vk_client=None):
#     if not mock_vk_client:
#         mock_response = AsyncMock()
#         mock_response.json.return_value = {"response": 1234567}  # Имитируем ответ от ВК
#
#         mock_client = AsyncMock()
#         mock_client.__aenter__.return_value.post.return_value = mock_response
#
#     with patch('httpx.AsyncClient', return_value=mock_client):
#         # Тестируем отправку сообщения
#         response = await send_message(
#             peer_id=123456,
#             text="Тестовое сообщение",
#             attachments=[]
#         )
#
#         # Проверяем, что был вызван метод post
#         mock_client.__aenter__.return_value.post.assert_called_once()
#
#         # Проверяем параметры вызова
#         call_args = mock_client.__aenter__.return_value.post.call_args
#         assert call_args[0][0] == "https://api.vk.com/method/messages.send"
#
#         # Проверяем, что возвращается правильный ответ
#         assert isinstance(response, PlainTextResponse)
#         assert response.body == b"ok"
#
# @pytest.mark.asyncio
# async def test_send_message_with_attachments(mock_vk_client=None):
#     if not mock_vk_client:
#         mock_response = AsyncMock()
#         mock_response.json.return_value = {"response": 1234567}
#
#         mock_client = AsyncMock()
#         mock_client.__aenter__.return_value.post.return_value = mock_response
#
#     with patch('httpx.AsyncClient', return_value=mock_client):
#         # Тестируем отправку сообщения с вложениями
#         await send_message(
#             peer_id=123456,
#             text="Тестовое сообщение с вложением",
#             attachments=["photo123_456"]
#         )
#
#         # Проверяем параметры вызова
#         call_args = mock_client.__aenter__.return_value.post.call_args[1]['params']
#         assert call_args['attachment'] == ["photo123_456"]
#         assert call_args['message'] == "Тестовое сообщение с вложением"
#         assert call_args['peer_id'] == 123456
#
#
# @pytest.mark.asyncio
# async def test_send_comment_to_vk(mock_vk_client=None):
#     if not mock_vk_client:
#         mock_response = AsyncMock()
#         mock_response.json.return_value = {"response": 1234567}  # Имитируем ответ от ВК
#
#         mock_client = AsyncMock()
#         mock_client.__aenter__.return_value.post.return_value = mock_response
#
#     with patch('httpx.AsyncClient', return_value=mock_client):
#         # Тестируем отправку сообщения
#         response = await send_comment(
#             post_id=123456,
#             text="Тестовое сообщение",
#         )
#
#         # Проверяем, что был вызван метод post
#         mock_client.__aenter__.return_value.post.assert_called_once()
#
#         # Проверяем параметры вызова
#         call_args = mock_client.__aenter__.return_value.post.call_args
#         assert call_args[0][0] == "https://api.vk.com/method/messages.send"
#
#         # Проверяем, что возвращается правильный ответ
#         assert isinstance(response, PlainTextResponse)
#         assert response.body == b"ok"
#
#
# if __name__ == "__main__":
#     print(asyncio.run(test_send_message_to_vk()))
#     print(asyncio.run(test_send_message_with_attachments()))
#     print(asyncio.run(test_send_comment_to_vk()))
#
