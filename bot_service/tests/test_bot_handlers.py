# модульные тесты работы хендлеров

import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, ANY

from app.bot.handlers import (
    start_handler, 
    help_handler, 
    token_handler, 
    llm_request_handler
)
from app.bot.keyboards.reply import GET_TOKEN_HELP_BUTTON_TEXT
from app.core.exceptions import ExpiredTokenError, InvalidTokenError

# token error cases for decode_and_validate mock
TOKEN_ERROR_CASES = [
    (ExpiredTokenError, 
     "⚠️ Токен истёк. Чтобы мы могли общаться, необходимо получить новый."),
    (InvalidTokenError, 
     "⚠️ Неверный токен. Чтобы мы могли общаться, необходимо получить новый."),
]

@pytest.mark.asyncio
async def test_start_handler():
    message = MagicMock()
    message.text = "start"
    message.from_user.first_name = "FakeUser"
    message.answer = AsyncMock()
    await start_handler(message)
    message.answer.assert_called()

@pytest.mark.asyncio
async def test_help_handler_with_help_command():
    message = MagicMock()
    message.text = "help"
    message.answer = AsyncMock()
    await help_handler(message)
    message.answer.assert_called()

@pytest.mark.asyncio
async def test_help_handler_with_keyboard_phrase():
    message = MagicMock()
    message.text = GET_TOKEN_HELP_BUTTON_TEXT
    message.answer = AsyncMock()
    await help_handler(message)
    message.answer.assert_called()

@pytest.mark.asyncio
async def test_token_handler_valid(monkeypatch, fake_async_redis):
    message = MagicMock()
    message.text = "/token valid_token"
    message.from_user.id = 7
    message.answer = AsyncMock()

    monkeypatch.setattr(
        "app.bot.handlers.decode_and_validate",
        lambda x: None
    )

    await token_handler(message)

    result = await fake_async_redis.get("token:7")
    assert result == b"valid_token"
    message.answer.assert_called_with(
        "✅ Токен сохранён. Теперь можно отправлять запросы модели!",
        reply_markup=ANY
    )

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_text",
    TOKEN_ERROR_CASES,
    ids=["expired_token", "invalid_token"]
)
async def test_token_invalid(monkeypatch, exception, expected_text):
    message = MagicMock()
    message.text = "/token invalid_token"
    message.from_user.id = 9
    message.answer = AsyncMock()

    def fake_decode(token):
        raise exception()

    monkeypatch.setattr(
        "app.bot.handlers.decode_and_validate",
        fake_decode
    )

    await token_handler(message)
    message.answer.assert_called_with(
        expected_text,
        reply_markup=ANY)

@pytest.mark.asyncio
async def test_llm_request_done(monkeypatch, fake_async_redis, delay_mock):
    message = MagicMock()
    message.text = "LLM text request"
    message.from_user.id = 1234
    message.chat.id = 345
    message.answer = AsyncMock()

    await fake_async_redis.set("token:1234", "valid_token")

    monkeypatch.setattr(
        "app.bot.handlers.decode_and_validate",
        lambda x: None
    )

    monkeypatch.setattr(
        "app.tasks.llm_tasks.get_system_prompt",
        lambda: "testing prompt"
    )

    await llm_request_handler(message)
    delay_mock.assert_called_once()
    message.answer.assert_called_with("Думаю... 🤔")


@pytest.mark.asyncio
async def test_llm_request_no_token_saved_request_not_sent(monkeypatch, delay_mock):
    message = MagicMock()
    message.text = "Some text"
    message.from_user.id = 12
    message.answer = AsyncMock()

    decode_mock = Mock()

    monkeypatch.setattr(
        "app.bot.handlers.decode_and_validate",
        decode_mock
    )

    await llm_request_handler(message)

    message.answer.assert_called_with(
        "Сначала отправь токен: /token <JWT>",
        reply_markup=ANY
    )

    decode_mock.assert_not_called()
    delay_mock.assert_not_called()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "exception, expected_text",
    TOKEN_ERROR_CASES,
    ids=["expired_token", "invalid_token"]
)
async def test_llm_request_invalid_token_request_not_sent(
    monkeypatch, 
    delay_mock,
    fake_async_redis,
    exception,
    expected_text
):
    message = MagicMock()
    message.text = "Some text which will never be sent"
    message.from_user.id = 123
    message.answer = AsyncMock()

    await fake_async_redis.set("token:123", "invalid_token")

    def fake_decode(token):
        raise exception()
    
    monkeypatch.setattr(
        "app.bot.handlers.decode_and_validate",
        fake_decode
    )

    await llm_request_handler(message)

    message.answer.assert_called_with(
        expected_text,
        reply_markup=ANY
    )

    delay_mock.assert_not_called()
