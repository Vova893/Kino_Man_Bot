"""
Инлайн-клавиатуры для Telegram-бота поиска фильмов.

Содержит все меню навигации:
- Главное меню поиска
- Параметры поиска по названию
- Toggle жанров (✅/☐)
- Количество результатов
- Рейтинги фильмов
"""


from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton


def main_search_menu() -> InlineKeyboardMarkup:
    """Главное меню типов поиска (5 кнопок в столбик).

    callback_data:
    - search_name — поиск по названию
    - search_rating — по рейтингу
    - search_low_budget — низкий бюджет
    - search_high_budget — высокий бюджет

    Returns:
        InlineKeyboardMarkup с row_width=1 (вертикальное меню)
    """
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton('🎬 Поиск по названию', callback_data='search_name'),
        InlineKeyboardButton('⭐ Поиск по рейтингу', callback_data='search_rating'),
        InlineKeyboardButton('💸 Низкий бюджет', callback_data='search_low_budget'),
        InlineKeyboardButton('💰 Высокий бюджет', callback_data='search_high_budget'),
    )
    return markup


def search_params_menu() -> InlineKeyboardMarkup:
    """Меню параметров поиска по названию фильма (5 кнопок).

    callback_data:
    - movie_title — ввод названия
    - choice_genre — выбор жанров
    - number_results — количество результатов
    - search_immediately — немедленный поиск
    - back_main — возврат в главное меню

    Returns:
        InlineKeyboardMarkup вертикальное меню
    """
    markup = InlineKeyboardMarkup(row_width=1)
    markup.add(
        InlineKeyboardButton('🎥 Ввести название фильма', callback_data='movie_title'),
        InlineKeyboardButton('🎭 Выбрать жанры', callback_data='choice_genre'),
        InlineKeyboardButton('🔢 Количество результатов', callback_data='number_results'),
        InlineKeyboardButton('🔍 Начать поиск', callback_data='search_immediately'),
        InlineKeyboardButton('🔙 Отмена', callback_data='back_main')
    )
    return markup


def genres_menu(selected_genres: str = '') -> InlineKeyboardMarkup:
    """Меню жанров с визуальным toggle (✅/☐).

    Args:
        selected_genres: строка вида 'боевик, драма' из БД

    Логика:
    - Парсит строку через split(',')
    - Добавляет ✅ для выбранных жанров
    - callback_data=genre_боевик для toggle

    Returns:
        InlineKeyboardMarkup(row_width=2) + Подтвердить/Назад
    """
    markup = InlineKeyboardMarkup(row_width=2)

    genres: dict[str, str] = {
        'боевик': '🦸‍♂️ Боевик',
        'комедия': '😂 Комедия',
        'драма': '🎭 Драма',
        'ужасы': '👻 Ужасы',
        'фантастика': '🚀 Фантастика',
        'романтика': '💕 Романтика'
    }

    buttons = []
    for genre_id, label in genres.items():
        # Проверяем наличие жанра в строке БД
        state = '✅' if genre_id in selected_genres.split(', ') else '☐'
        buttons.append(InlineKeyboardButton(
            f'{state} {label}',
            callback_data=f'genre_{genre_id}'
        ))

    markup.add(*buttons)
    markup.row(
        InlineKeyboardButton('✅ Подтвердить', callback_data='genres_confirm'),
        InlineKeyboardButton('🔙 Назад', callback_data='back')
    )
    return markup


def count_menu() -> InlineKeyboardMarkup:
    """Меню выбора количества результатов (3, 5, 10, 20).

    callback_data: count_3, count_5, count_10, count_20

    Returns:
        InlineKeyboardMarkup с 5 кнопками (4+Назад)
    """
    markup = InlineKeyboardMarkup(row_width=1)
    for count in [3, 5, 10, 20]:
        markup.add(
            InlineKeyboardButton(
                f'{count} результатов',
                callback_data=f'count_{count}'
            )
        )
    markup.add(InlineKeyboardButton('🔙 Назад', callback_data='back'))
    return markup


def rating_menu() -> InlineKeyboardMarkup:
    """Меню минимального рейтинга фильмов (6.0+ до 8.0+).

    callback_data: rating_6, rating_6.5, rating_7, rating_7.5, rating_8

    Returns:
        InlineKeyboardMarkup с 6 кнопками (5 рейтингов+Отмена)
    """
    markup = InlineKeyboardMarkup(row_width=1)
    ratings: list[tuple[str, str]] = [
        ('⭐ 8.0+', 'rating_8'),
        ('⭐ 7.5+', 'rating_7.5'),
        ('⭐ 7.0+', 'rating_7'),
        ('⭐ 6.5+', 'rating_6.5'),
        ('⭐ 6.0+', 'rating_6')
    ]

    for label, rating_id in ratings:
        markup.add(InlineKeyboardButton(label, callback_data=rating_id))

    markup.add(InlineKeyboardButton('🔙 Отмена', callback_data='back_main'))
    return markup
