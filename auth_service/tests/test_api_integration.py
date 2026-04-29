# Интеграционные тесты

import pytest
from httpx import AsyncClient

# Полный цикл: register -> login -> me
@pytest.mark.asyncio
async def test_register_login_get_me(client: AsyncClient):
    email = "test_user@email.com"
    password = "test_password"
    
    # register
    register_response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password
        }
    )
    # проверки 
    assert register_response.status_code == 201
    data = register_response.json()
    assert data["email"] == email
    assert "id" in data
    assert "role" in data
    assert "created_at" in data

    # login (OAuth2, form-data)
    login_response = await client.post(
        "/auth/login",
        data={
            "username": email,
            "password": password
        }
    )
    # проверки
    assert login_response.status_code == 200
    token_data = login_response.json()
    assert "access_token" in token_data
    assert token_data["token_type"] == "bearer"
    token = token_data["access_token"] 

    # доступ к защищенному ендпоинту me
    me_response = await client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert me_response.status_code == 200

    data = me_response.json()
    assert data["email"] == email
    assert "id" in data
    assert "created_at" in data


# регистрация пользователя по уже зарегистрированному email возвращает ошибку 409
@pytest.mark.asyncio
async def test_register_existing_user_raises_409(client: AsyncClient):
    payload = {
        "email": "user_exists@email.com",
        "password": "password_supersecret"
    }

    # Первая попытка регистрации - успешная 
    response = await client.post("/auth/register", json=payload)
    assert response.status_code == 201

    # Вторая попытка регистрации - должна упасть
    response2 = await client.post("/auth/register", json=payload)
    assert response2.status_code == 409
    assert response2.json()["detail"] == "Пользователь с таким email уже существует."


# логин с неверным паролем возвращает ошибку 401
@pytest.mark.asyncio
async def test_login_with_wrong_password_raises_401(client: AsyncClient):
    email = "test_wrong_pass@email.com"
    true_pass = "true_pass"
    wrong_pass = "wrong_pass"

    # предварительная регистрация 
    register_response = await client.post(
        "/auth/register",
        json={
            "email": email,
            "password": true_pass
        }
    )
    assert register_response.status_code == 201

    # вход с неверным паролем
    login_response = await client.post(
        "/auth/login",
        data={
            "username": email,
            "password": wrong_pass
        }
    )
    # проверка: исклбчение 401 и токен не был выдан
    assert login_response.status_code == 401
    data = login_response.json()
    assert data["detail"] == "Неверный email или пароль."


# логин с неверным email возвращает ошибку 401
@pytest.mark.asyncio
async def test_login_with_unregistered_email_raises_401(client: AsyncClient):
    login_response = await client.post(
        "/auth/login",
        data={
            "username": "unregistered@email.com",
            "password": "test_password"
        }
    )
    assert login_response.status_code == 401
    data = login_response.json()
    assert data["detail"] == "Неверный email или пароль."


# запрос к /auth/me с неверным токеном возвращает 401
@pytest.mark.asyncio
async def test_auth_me_with_invalid_token_raises_401(client: AsyncClient):
    me_response = await client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer wrong-token"
        }
    )
    assert me_response.status_code == 401
    assert me_response.json()["detail"] == "Невалидный токен."

# запрос с /auth/me без токена возвращает 401
@pytest.mark.asyncio
async def test_auth_me_without_token_raises_401(client: AsyncClient):
    me_response = await client.get("/auth/me")
    assert me_response.status_code == 401
