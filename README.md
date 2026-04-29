# Двухсервисная система LLM-консультаций посредством Telegram-бота

Проект представляет из себя распределённую систему, состоящую из двух логически и технически независимых сервисов: Auth Service & Bot Service.

- `Auth Service` отвечает исключительно за аутентификацию и выпуск токенов.
- `Bot Service` отвечает за предоставление функциональности LLM-консультаций через Telegram-бота.

Сценарий работы:

- Пользователь регистрируется, входит в систему и получает JWT-токен через Auth Service.
- Отправляет полученный токен телеграм боту и получает возможность отправлять запросы LLM модели.

Подробнее о работе каждого сервиса будет изложено ниже, после инструкции по поднятию проекта в Docker

## Установка проекта

1. (Если у Вас Windows) Необходимо установить WSL2 & Docker Dekstop

Подробнее о шагах установки Вы можете ознакомиться, перейдя по ссылкам:

- Docker Desktop: https://www.docker.com/products/docker-desktop/
- WSL2: https://learn.microsoft.com/en-us/windows/wsl/install


2. Скачайте проект локально:

```bash
git clone https://github.com/lizofeta/llm-tg-bot.git 
```

3. Перейдите в корневую директорию проекта:

```bash
cd путь_к_директории_проекта_на_вашем_пк
```

- Настройка переменных файла .env сервиса Bot Service:

    1. Перейдите в `bot_service`:
    ```bash
    cd bot_service
    ```
    2. Откройте файл `.env.example` и заполните следующие поля:
    ```env
    TELEGRAM_BOT_TOKEN=
    OPENROUTER_API_KEY=
    JWT_SECRET=
    ```
    3. Переименуйте файл `.env.example` в `.env`
    ```bash
    mv .env.example .env
    ```

-  Настройка переменных файла .env сервиса Auth Service:
    1. Перейдите в `auth_service`:
    ```bash
    cd ../auth_service
    ```
    2. Откройте файл `.env.example` и заполните следующие поля:
    ```env
    JWT_SECRET=
    ```
    3. Переименуйте файл `.env.example` в `.env`
    ```bash
    mv .env.example .env
    ```

5. Перейдите в корень проекта и выполните команду `docker compose up --build`:

```bash
cd ..
docker compose up --build
```

- Auth Service Swagger: http://localhost:8000/docs
- Bot Service FastAPI: http://localhost:8001
- RabbitMQ: http://localhost:15672

## Auth Service 

Сервис предназначен для авторизации пользователей в системе и выдачи JWT-токенов, без которых доступ к функциональности бота не предоставляется.

### Регистрация

![register_endpoint](/screenshots/register_endpoint.png)

### Авторизация

![login_endpoint](/screenshots/login_endpoint.png)

### Авторизация через Swagger

![swagger_authorization](/screenshots/swagger_authorization.png)

### Endpoint получения текущего пользователя

![me_endpoint](/screenshots/me_endpoint.png)


## Telegram Bot

Сервис предоставляет функциональность LLM-консультаций посредством телеграм бота. 

Запросы к внешнему API обрабатываются асинхронно с использованием `Celery`:
- В качестве брокера сообщений использован `RabbitMQ`
- В качестве хранилища состояний и результатов задач использован `Redis`

### Общий пример общения с ботом

![chat example](/screenshots/chat_example.png)

### Подробнее о получении токена и функциональности бота:

![get_token](/screenshots/get_token.png)

### Общение с ботом

Пользователю предлагаются примеры вопросов боту в виде кнопок:

![question_examples](/screenshots/question_examples.png)


### RabbitMQ

![rabbitmq](/screenshots/rabbitmq.png)

## Тестирование

Запуск тестирования:
```bash
python -m pytest -v
```

### Auth Service

![auth service tests](/screenshots/test_auth_service.png)

### Bot Service

![bot service tests](/screenshots/test_bot_service.png)
