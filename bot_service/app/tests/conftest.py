import pytest
import fakeredis
from unittest.mock import MagicMock

from app.core.exceptions import ExpiredTokenError, InvalidTokenError

# redis mocking

@pytest.fixture
def fake_redis_server():
    return fakeredis.FakeServer()

@pytest.fixture
def fake_async_redis(fake_redis_server):
    return fakeredis.FakeAsyncRedis(server=fake_redis_server)

@pytest.fixture
def fake_sync_redis(fake_redis_server):
    return fakeredis.FakeStrictRedis(server=fake_redis_server)

@pytest.fixture(autouse=True)
def patch_async_redis(monkeypatch, fake_async_redis, fake_sync_redis):

    monkeypatch.setattr(
        "app.bot.handlers.redis_client",
        fake_async_redis
    )

    monkeypatch.setattr(
        "app.bot.redis_listener.redis_client",
        fake_async_redis
    )

    monkeypatch.setattr(
        "app.tasks.llm_tasks.sync_redis_client",
        fake_sync_redis
    )

# llm_request.delay mock

@pytest.fixture
def delay_mock():
    return MagicMock()

@pytest.fixture(autouse=True)
def patch_delay_mock(monkeypatch, delay_mock):
    monkeypatch.setattr(
        "app.bot.handlers.llm_request.delay",
        delay_mock
    )
