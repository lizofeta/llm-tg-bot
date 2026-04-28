from aiogram import Router, F 
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.filters import Command

from app.core.jwt import decode_and_validate
from app.core.exceptions import ExpiredTokenError, InvalidTokenError
from app.infra.redis import redis_client
from app.tasks.llm_tasks import llm_request
from app.bot.keyboards.reply import (
    GET_TOKEN_HELP_BUTTON_TEXT, 
    info_keyboard, 
    question_examples
)

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    user_name = message.from_user.first_name
    await message.answer(
        text=(f"Привет, {user_name}! 😊 Я - дружелюбный бот " 
        "с доступом к большой языковой модели по JWT-токену\n"
        "Чтобы я смог тебе отвечать, тебе нужен токен доступа.\n\n"
        "Чтоб узнать, как получить токен, используй команду /help " 
        "или нажми кнопку ниже 👇"),
        reply_markup=info_keyboard()
    )

@router.message(Command("help"))
@router.message(F.text == GET_TOKEN_HELP_BUTTON_TEXT)
async def help_handler(message: Message):
    await message.answer(
        text=("Следуй инструкции, чтобы получить токен и я смог тебе отвечать:\n\n"
        "Шаги:\n\n"
        "1. Открой http://localhost:8000/docs\n\n"
        "2. Зарегистрируйся: register\n\n"
        "3. Войди: login\n\n"
        "4. Скопируй access_token\n\n"
        "5. Отправь его мне командой: /token <твой токен>\n\n"
        "Готово! 🙌🏻"),
        reply_markup=info_keyboard()
    )


@router.message(Command("token"))
async def token_handler(message: Message):
    # Проверка валидности ввода и парсинг
    parts = message.text.split(maxsplit=1)

    if len(parts) != 2:
        await message.answer(
            "Используй: /token <JWT>",
            reply_markup=ReplyKeyboardRemove()
        )
        return
    
    token = parts[1].strip()

    # Проверка валидности токена
    try:
        decode_and_validate(token)
    except ExpiredTokenError:
        await message.answer(
            "⚠️ Токен истёк. Чтобы мы могли общаться, необходимо получить новый.",
            reply_markup=info_keyboard()
        )
        return
    except InvalidTokenError:
        await message.answer(
            "⚠️ Неверный токен. Чтобы мы могли общаться, необходимо получить новый.",
            reply_markup=info_keyboard()
        )
        return
    
    # Сохранение токена в Redis
    await redis_client.set(
        f"token:{message.from_user.id}",
        token,
        ex=3600
    )

    await message.answer(
        "✅ Токен сохранён. Теперь можно отправлять запросы модели!",
        reply_markup=question_examples()
    )


@router.message()
async def llm_request_handler(message: Message):
    # Проверка наличия токена в Redis
    user_id = message.from_user.id
    token = await redis_client.get(f"token:{user_id}")
    if token is None:
        await message.answer(
            "Сначала отправь токен: /token <JWT>",
            reply_markup=info_keyboard()
        )
        return
    if isinstance(token, bytes):
        token = token.decode()

    # Проверка валидности токена
    try:
        decode_and_validate(token)
    except ExpiredTokenError:
        await message.answer(
            "⚠️ Токен истёк. Чтобы мы могли общаться, необходимо получить новый.",
            reply_markup=info_keyboard()
        )
        return
    except InvalidTokenError:
        await message.answer(
            "⚠️ Неверный токен. Чтобы мы могли общаться, необходимо получить новый.",
            reply_markup=info_keyboard()
        )
        return
    # Отправка запроса модели
    llm_request.delay(message.chat.id, message.text)
    await message.answer("Думаю... 🤔")
