"""
Обработчик выбора минимального рейтинга фильмов для Telegram-бота.

Функционал:
- Выбор рейтинга
- Сохранение в БД поле rating
- Немедленный поиск фильмов с выбранным рейтингом
"""


from telebot.types import CallbackQuery  # type: ignore
from loader import bot
from database.database import (register_user_if_not_exists, log_button_click, log_action, MovieSearchPreferences)
from site_API.api_client import poisk_kino_api_rating
from utils.movie_messages import movie_messages


@bot.callback_query_handler(func=lambda call: call.data.startswith('rating_'))
def click_inline_button(call):
    """Функция обработки нажатия inline-кнопок выбора рейтинга

       Алгоритм:
       1. Парсит рейтинг из callback_data
       2. Сохраняет в MovieSearchPreferences.rating
       3. Выполняет немедленный поиск по API
       4. Отправляет результаты через movie_messages

       Args:
           call: CallbackQuery вида 'rating_6', 'rating_7', 'rating_8'
       """
    chat_id = call.message.chat.id
    user = register_user_if_not_exists(call.from_user)
    log_button_click(user, call.data)

    # Обрабатываем выбор рейтинга
    if call.data.startswith('rating_'):
        # Извлекаем количество результатов из callback-data
        rating_result = call.data.replace('rating_', '')

        # Сохраняем выбранный рейтинг результатов в базу данных
        preferences, _ = MovieSearchPreferences.get_or_create(user=user)
        preferences.rating = rating_result
        preferences.save()

        messages = poisk_kino_api_rating(user)
        movie_messages(messages, call)
        log_action(user, 'rating_', details=f'Фильмы с рейтингом: {rating_result}')
