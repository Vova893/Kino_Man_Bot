"""
Обработчик жанров фильмов для Telegram-бота.
Динамическое меню с переключением состояний ✅/☐ жанров.

Функционал:
- Множественный выбор жанров с визуальной обратной связью
- Сохранение в БД как строку 'боевик, драма, ужасы'
- Интерактивное обновление клавиатуры без перезагрузки
"""

from typing import Set
from telebot.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot
from database.database import (
    register_user_if_not_exists,
    log_button_click,
    log_action,
    MovieSearchPreferences
)


def update_genres_menu(
        chat_id: int,
        current_genres: Set[str]
) -> InlineKeyboardMarkup:
    """Создает/обновляет клавиатуру жанров с визуальными отметками.

    Args:
        chat_id: ID чата для контекста
        current_genres: set[str] выбранных жанров (без UI символов)

    Returns:
        InlineKeyboardMarkup с кнопками ✅/☐ + Подтвердить/Назад
    """
    markup = InlineKeyboardMarkup(row_width=2)

    # Словарь жанров: id → emoji + label
    genres: dict[str, str] = {
        'боевик': '🦸‍♂️ Боевик',
        'комедия': '😂 Комедия',
        'драма': '🎭 Драма',
        'ужасы': '👻 Ужасы',
        'фантастика': '🚀 Фантастика',
        'романтика': '💕 Романтика'
    }

    # Создаем кнопки с состоянием ✅/☐
    buttons = []
    for genre_id, label in genres.items():
        state = '✅' if genre_id in current_genres else '☐'
        buttons.append(InlineKeyboardButton(
            f'{state} {label}',
            callback_data=f'genre_{genre_id}'
        ))

    markup.add(*buttons)
    markup.row(
        InlineKeyboardButton('✅ Подтвердить', callback_data='confirm_genres'),
        InlineKeyboardButton('🔙 Назад', callback_data='back')
    )

    return markup


@bot.callback_query_handler(func=lambda call: call.data.startswith('genre_'))
def click_inline_button(call: 'CallbackQuery') -> None:
    """Обрабатывает выбор жанров (toggle ✅/☐).

    Логика:
    1. Toggle жанра в множественном выборе
    2. Сохранение в БД как 'боевик, драма, ужасы'
    3. Динамическое обновление клавиатуры
    4. Логирование изменений

    Args:
        call: CallbackQuery от кнопки genre_*
    """
    chat_id = call.message.chat.id
    user = register_user_if_not_exists(call.from_user)
    log_button_click(user, call.data)

    # Загружаем текущие жанры пользователя
    prefs, _ = MovieSearchPreferences.get_or_create(user=user)
    saved_genres: Set[str] = set()

    if prefs.genres:
        saved_genres = set(prefs.genres.split(', '))

    # Toggle выбранного жанра
    genre_id: str = call.data.replace('genre_', '')

    if genre_id in saved_genres:
        saved_genres.remove(genre_id)
        log_action(user, 'genre_removed', details=genre_id)
    else:
        saved_genres.add(genre_id)
        log_action(user, 'genre_added', details=genre_id)

    # Сохраняем в БД (строка или NULL)
    prefs.genres = ', '.join(saved_genres) if saved_genres else None
    prefs.save()

    #  Динамически обновляем клавиатуру
    updated_markup = update_genres_menu(chat_id, saved_genres)
    bot.edit_message_reply_markup(
        chat_id=chat_id,
        message_id=call.message.message_id,
        reply_markup=updated_markup
    )

    log_action(user, 'genres_updated', details=f'{saved_genres}')
