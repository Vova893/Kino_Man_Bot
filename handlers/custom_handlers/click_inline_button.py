"""
Обработчики callback_query и текстового ввода для Telegram-бота поиска фильмов.

Поддерживает:
- Навигацию по меню поиска (название, жанры, рейтинг, бюджет)
- Сохранение параметров поиска в БД
- Логирование всех действий пользователя
- Поиск по API Kinopoisk/фильмы

Зависимости:
- telebot (pyTelegramBotAPI)
- database.database (Peewee модели)
- keyboards.inline.search_menu
- site_API.api_client (Kinopoisk API)
"""
from loader import bot
from telebot.types import Message, CallbackQuery
from keyboards.inline.search_menu import (search_params_menu, rating_menu,
                                          main_search_menu, genres_menu, count_menu)
from database.database import (register_user_if_not_exists, log_button_click,
                               log_action, database, InlineButtonClick, MovieSearchPreferences)
from site_API.api_client import (poisk_kino_api_name, poisk_kino_api, poisk_kino_api_low_budget,
                                 poisk_kino_api_high_budget)
from utils.movie_messages import movie_messages


def handle_input_text(message: Message) -> None:
    """Обрабатывает текстовый ввод пользователя после нажатия кнопки.

    Логика:
    1. Регистрирует пользователя и логирует ввод
    2. Привязывает текст к последнему нажатию кнопки (без input_value)
    3. Сохраняет как movie_title в предпочтениях
    4. Выполняет поиск по названию

    Args:
        message: telebot.types.Message с текстом пользователя
    """
    user = register_user_if_not_exists(message.from_user)
    log_action(user, 'received_input', details=message.text)

    with database.atomic():
        # Находим последнее нажатие кнопки БЕЗ привязанного текста
        click_record = (InlineButtonClick
                        .select()
                        .where((InlineButtonClick.user == user) &
                               (InlineButtonClick.input_value.is_null(True)))
                        .order_by(InlineButtonClick.timestamp.desc())
                        .limit(1)
                        .get())

        click_record.input_value = message.text
        click_record.save()

        # Сохраняем название фильма
        prefs, _ = MovieSearchPreferences.get_or_create(user=user)
        prefs.movie_title = message.text  # Меняем только название фильма
        prefs.save()

    messages = poisk_kino_api_name(message.text, user)
    movie_messages(messages, message)


@bot.callback_query_handler(func=lambda call: not call.data.startswith('genre_')
                                              and not call.data.startswith('count_')
                                              and not call.data.startswith('rating_')
                                              and not call.data.startswith('history_')
                                              and not call.data.startswith('page_')
                                              and not call.data == 'main_menu')
def click_inline_button(call: CallbackQuery) -> None:
    """Центральный обработчик всех inline-кнопок (кроме жанров/количества).

    Args:
        call: telebot.types.CallbackQuery от нажатия кнопки
    """

    # Обязательный ответ на callback_query!
    try:
        bot.answer_callback_query(call.id)
    except:
        pass

    user = register_user_if_not_exists(
        call.from_user)  # Проверяется существование пользователя, если его нет то регистрируется
    log_button_click(user, call.data)  # Создается журнал действия нажатий inline-кнопок

    # обработка нажатий на inline-кнопку "Поиск по названию"
    if call.data == 'search_name':
        bot.edit_message_text(
            'Укажите параметры поиска: ',
            call.message.chat.id,
            call.message.message_id,
            reply_markup=search_params_menu()
        )
        log_action(user, 'search_name', details='Нажата кнопка "Поиск по названию"')
    # обработка нажатий на inline-кнопку "Поиск по рейтингу"
    elif call.data == 'search_rating':
        bot.edit_message_text(
            'По какому рейтингу ищем? ',
            call.message.chat.id,
            call.message.message_id,
            reply_markup=rating_menu()
        )
        log_action(user, 'search_rating', details='Нажата кнопка "Поиск по рейтингу"')

    # обработка нажатий на inline-кнопку "Низкий бюджет"
    elif call.data == 'search_low_budget':
        messages = poisk_kino_api_low_budget(user)
        movie_messages(messages, call)
        log_action(user, 'search_low_budget', details='Нажата кнопка "Низкий бюджет"')

    # обработка нажатий на inline-кнопку "Высокий бюджет"
    elif call.data == 'search_high_budget':
        messages = poisk_kino_api_high_budget(user)
        movie_messages(messages, call)
        log_action(user, 'search_high_budget', details='Нажата кнопка "Высокий бюджет"')

    # обработка нажатий на inline-кнопку "Главное меню"
    elif call.data == 'back_main':
        bot.edit_message_text(
            'Главное меню: ',
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_search_menu()
        )
        log_action(user, 'back_main', details='Нажата кнопка "Главное меню"')

    # обработка нажатий на inline-кнопки после нажатия кнопки "Поиск по названию"
    # обработка нажатий на inline-кнопку "Ввести название фильма"
    elif call.data == 'movie_title':
        bot.edit_message_text(
            '🎥 Введите название фильма:',
            call.message.chat.id,
            call.message.message_id,
            reply_markup=None
        )
        log_action(user, 'movie_title', details='Нажата кнопка "Ввести название фильма"')
        bot.register_next_step_handler_by_chat_id(call.message.chat.id, handle_input_text)

    # обработка нажатий на inline-кнопку "Выбрать жанры"
    elif call.data == 'choice_genre':
        bot.edit_message_text(
            '🎬 Выберите жанры фильмов:',
            call.message.chat.id,
            call.message.message_id,
            reply_markup=genres_menu()
        )
        log_action(user, 'choice_genre', details='Нажата кнопка "Выбрать жанры"')

    # обработка нажатий на inline-кнопку "Количество результатов"
    elif call.data == 'number_results':
        bot.edit_message_text(
            '📊 Выберите количество результатов:',
            call.message.chat.id,
            call.message.message_id,
            reply_markup=count_menu()
        )
        log_action(user, 'number_results', details='Нажата кнопка "Количество результатов"')

    # обработка нажатий на inline-кнопку "Начать поиск"
    elif call.data == 'search_immediately':
        messages = poisk_kino_api(user)
        movie_messages(messages, call)
        log_action(user, 'search_immediately', details='Нажата кнопка "Начать поиск"')

    # обработка нажатий на inline-кнопку "Отмена"
    elif call.data == 'back_main':
        bot.edit_message_text(
            '🎬 Главное меню',
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_search_menu()
        )
        log_action(user, 'back_main', details='Нажата кнопка "Отмена"')

    # обработка нажатий на inline-кнопку "Назад"
    elif call.data == 'back':
        bot.edit_message_text(
            'Меню параметров поиска',
            call.message.chat.id,
            call.message.message_id,
            reply_markup=search_params_menu()
        )
        log_action(user, 'back', details='Нажата кнопка "Назад"')

    # обработка нажатий на inline-кнопку "Подтвердить"
    elif call.data == 'confirm_genres':
        bot.edit_message_text(
            f'✅ Ваши предпочтения жанров были сохранены.\nВыбирайте другие параметры или приступайте к поиску.',
            call.message.chat.id,
            call.message.message_id,
            reply_markup=search_params_menu()
        )
        log_action(user, 'genres_confirmed', details='Жанры подтверждены')
