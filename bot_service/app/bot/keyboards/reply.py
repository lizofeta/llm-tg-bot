from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

GET_TOKEN_HELP_BUTTON_TEXT = "Как получить токен?"

def info_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=GET_TOKEN_HELP_BUTTON_TEXT)]
        ],
        resize_keyboard=True
    )

def question_examples():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🌐 Как работает интернет?")],
            [KeyboardButton(text="💻 Кто придумал Python?")],
            [KeyboardButton(text="🧠 Как навсегда запомнить выученное?")],
            [KeyboardButton(text="🖼️ Чем импрессионизм отличается от реализма?")]
        ],
        resize_keyboard=True
    )
