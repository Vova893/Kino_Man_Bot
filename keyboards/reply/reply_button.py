"""
Reply клавиатура (обычные кнопки под полем ввода) для Telegram-бота.

Содержит основные действия:
- 🔍 Поиск фильмов → main_search_menu()
- 📜 История → search_history_command()
"""

from telebot import types


def repli_button() -> types.ReplyKeyboardMarkup:
    """Создает постоянную reply клавиатуру с основными функциями.

    Параметры клавиатуры:
    - resize_keyboard=True — подстраивает высоту под содержимое
    - one_time_keyboard=False — клавиатура постоянная (не исчезает)
    - selective=False — показывается всем (не только упомянутым)

    Кнопки:
    - 🔍 Поиск фильмов
    - 📜 История

    Returns:
        types.ReplyKeyboardMarkup — готовая клавиатура для reply_markup
    """
    markup = types.ReplyKeyboardMarkup(
        resize_keyboard=True,  # Автоподбор размера
        one_time_keyboard=False,  # Постоянная (не одноразовая)
        selective=False  # Видна всем участникам чата
    )

    # Создаем кнопки
    movie_search = types.KeyboardButton('🔍 Поиск фильмов')
    history_btn = types.KeyboardButton('📜 История')

    # Добавляем в markup (2 кнопки в ряд)
    markup.add(movie_search, history_btn)

    return markup
