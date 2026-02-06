"""
Обработчик выбора количества результатов поиска для Telegram-бота фильмов.

Функционал:
- Выбор количества выводимых результатов (5, 10, 20, 50)
- Сохранение в БД поле result_count
- Подтверждение выбора + переход к следующим параметрам
"""


from telebot.types import CallbackQuery  # type: ignore
from loader import bot
from database.database import (
    register_user_if_not_exists,
    log_button_click,
    log_action,
    MovieSearchPreferences
)
from keyboards.inline.search_menu import search_params_menu


@bot.callback_query_handler(func=lambda call: call.data.startswith('count_'))
def click_inline_button(call: 'CallbackQuery') -> None:
    """Обрабатывает выбор количества результатов поиска (count_*).

    Алгоритм:
    1. Парсит число из callback_data ('count_10' → 10)
    2. Сохраняет в MovieSearchPreferences.result_count
    3. Показывает подтверждение + меню следующих параметров
    4. Логирует выбор пользователя

    Args:
        call: CallbackQuery с данными вида 'count_5', 'count_10', 'count_20'
    """
    chat_id: int = call.message.chat.id
    user = register_user_if_not_exists(call.from_user)
    log_button_click(user, call.data)

    # Извлекаем количество из callback_data
    result_count: int = int(call.data.replace('count_', ''))

    # Сохраняем в БД
    preferences, _ = MovieSearchPreferences.get_or_create(user=user)
    preferences.result_count = result_count
    preferences.save()

    # Подтверждение выбора + следующие шаги
    bot.edit_message_text(
        f'📊 Количество результатов: <b>{result_count}</b>\n\n'
        f'✅ Настройка сохранена!\n'
        f'Выберите другие параметры или <b>"Начать поиск"</b>',
        chat_id,
        call.message.message_id,
        parse_mode='HTML',
        reply_markup=search_params_menu()
    )

    log_action(
        user,
        'count_selected',
        details=f'result_count={result_count}'
    )

