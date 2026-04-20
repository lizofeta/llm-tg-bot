# модульные тесты для ключевой логики Auth Service

from unittest.mock import Mock, AsyncMock

import pytest 

from app.core.exceptions import (
    InvalidCredentialsError, 
    UserAlreadyExistsError,
    InvalidTokenError    
)
from app.db.models import User 
from app.usecases.auth import AuthUseCase

@pytest.mark.asyncio
async def test_register_hash_password_create_user(monkeypatch, settings):
    repository = Mock()
    # Ожидаем, что пользователь с указанным email еще не зарегистрирован:
    repository.get_user_by_email = AsyncMock(return_value=None)
    # Передаем пользователя, если он будет создан:
    created_user = User(id=5, email="test_example@email.com", password_hash="hashed-pwd")
    repository.create_user = AsyncMock(return_value=created_user)

    # симуляция хеширования пароля:
    monkeypatch.setattr(
        "app.usecases.auth.hash_password",
        lambda pwd: f"hashed::{pwd}"
    )

    # регистрация 
    usecase = AuthUseCase(repository, settings)
    new_user = await usecase.register("test_example@email.com", "plain-password")

    # проверки
    assert new_user is created_user
    repository.get_user_by_email.assert_called_once_with("test_example@email.com")
    repository.create_user.assert_called_once_with(
        "test_example@email.com",
        "hashed::plain-password"
    )


@pytest.mark.asyncio
async def test_register_raises_email_already_exist(settings):
    repository = Mock()

    # пользователь с указанным email найден в БД:
    repository.get_user_by_email = AsyncMock(return_value = User(
        id=1,
        email="taken@email.com",
        password_hash="hashed-pwd"
    ))

    usecase = AuthUseCase(repository, settings)

    # проверка, что было выброшено исключение:
    with pytest.raises(UserAlreadyExistsError):
        await usecase.register(
            email="taken@email.com",
            password="qwerty12345"
        )
    
    # проверка, что функция создания нового пользователя не была вызвана:
    repository.create_user.assert_not_called()


@pytest.mark.asyncio
async def test_login_returns_token(monkeypatch, settings):
    repository = Mock()
    user = User(id=2, email="user2@email.com", password_hash="hashed-pwd")
    repository.get_user_by_email = AsyncMock(return_value=user)

    monkeypatch.setattr(
        "app.usecases.auth.verify_password",
        lambda **_: True
    )

    monkeypatch.setattr(
        "app.usecases.auth.create_access_token",
        lambda **kwargs: f"token-for-user-{kwargs['data']['sub']}"
    )

    usecase = AuthUseCase(repository, settings)

    token = await usecase.login(
        email="user2@email.com",
        password="qwerty1234"
    )

    assert token == "token-for-user-2"
    repository.get_user_by_email.assert_called_once_with("user2@email.com")


@pytest.mark.asyncio
async def test_login_raises_for_unknown_user(monkeypatch, settings):
    repository = Mock()
    # пользователь с указанным email не найден:
    repository.get_user_by_email = AsyncMock(return_value=None)
    usecase = AuthUseCase(repository, settings)

    # токен, который не должен быть выдан:
    mocked_token = Mock()
    monkeypatch.setattr(
        "app.usecases.auth.create_access_token",
        mocked_token
    )
    
    # проверка вызова исключения:
    with pytest.raises(InvalidCredentialsError):
        await usecase.login("unknown@email.com", "qwerty1234")
    
    # проверка, что токен не был выдан:
    mocked_token.assert_not_called()
    # проверка обращения к БД с верными аргументами:
    repository.get_user_by_email.assert_called_once_with("unknown@email.com")


@pytest.mark.asyncio
async def test_login_raises_wrong_password(monkeypatch, settings):
    repository = Mock()

    # пользователь существует 
    repository.get_user_by_email = AsyncMock(return_value = User(
        id=7,
        email="user7@email.com",
        password_hash="hashed-pwd"
    ))

    # неверный пароль
    monkeypatch.setattr(
        "app.usecases.auth.verify_password",
        lambda **_: False
    )

    # мок для токена 
    mocked_token = Mock()
    monkeypatch.setattr(
        "app.usecases.auth.create_access_token",
        mocked_token
    )

    usecase = AuthUseCase(repository, settings)

    # вызвано исключение 
    with pytest.raises(InvalidCredentialsError):
        await usecase.login("user7@email.com", "wrong-password")
    
    # токен не был выдан
    mocked_token.assert_not_called()
    # проверка вызова функции получения пользователя по email
    repository.get_user_by_email.assert_called_once_with("user7@email.com")


@pytest.mark.asyncio
async def test_me_returns_current_user(monkeypatch, settings):
    repository = Mock()

    # текущий пользователь
    current_user = User(
        id=8,
        email="current@email.com",
        password_hash="qwerty1234"
    )
    repository.get_user_by_id = AsyncMock(return_value = current_user)

    # функция декодирования в payload возвращает id текущего пользователя
    monkeypatch.setattr(
        "app.usecases.auth.decode_token",
        lambda **kwargs: {"sub": "8"}
    )

    usecase = AuthUseCase(repository, settings)

    user = await usecase.me("token-for-user-8")
    
    # проверки
    assert user is current_user
    repository.get_user_by_id.assert_called_once_with(8)


@pytest.mark.asyncio
async def test_me_raises_for_invalid_token(monkeypatch, settings):
    repository = Mock()

    # функция декодирования токена возвращает sub = None
    monkeypatch.setattr(
        "app.usecases.auth.decode_token",
        lambda **_: {"sub": None}
    )

    usecase = AuthUseCase(repository, settings)
    
    # проверка на вызов исключения:
    with pytest.raises(InvalidTokenError):
        await usecase.me(token="invalid-token")
    
    # обращения к БД не произошло:
    repository.get_user_by_id.assert_not_called()
