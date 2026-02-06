"""
Модуль моделей базы данных для Telegram-бота по поиску фильмов.

Содержит:
- Модели Peewee для SQLite: пользователи, логи действий, история поиска
- Функции создания таблиц и логирования активности
- Автоматическую регистрацию пользователей

Зависимости:
- peewee
- loader.database (SQLite connection)
- datetime

Структура БД:
User (1:*) → UserActionLog, InlineButtonClick, MovieSearchPreferences, SearchHistory
"""
from peewee import *
from datetime import datetime
from typing import Optional, Union
from loader import database



# Базовый класс для наших моделей
class BaseModel(Model):
    """Базовая модель со связанной БД"""

    class Meta:
        database: 'SqliteDatabase' = database  # type: ignore[assignment]


class User(BaseModel):
    """Модель пользователя Telegram"""

    telegram_id: 'BigIntegerField' = BigIntegerField(primary_key=True)  # ID пользователя Telegram
    username: 'CharField' = CharField(null=True)  # Имя пользователя (никнейм)
    first_name: 'CharField' = CharField(null=True)  # Первое имя
    last_name: 'CharField' = CharField(null=True)  # Фамилия пользователя


class UserActionLog(BaseModel):
    """Лог действий пользователя (команды, ввод текста)"""

    user: 'ForeignKeyField' = ForeignKeyField(User, backref='actions')  # Связь с моделью User
    action_type: 'CharField' = CharField()  # Тип действия (команда, ввод)
    details: 'TextField' = TextField(null=True)  # Дополнительные подробности действия
    timestamp: 'DateTimeField' = DateTimeField(default=datetime.now)  # Время события


class InlineButtonClick(BaseModel):
    """Логирование нажатий inline-кнопок"""

    user: 'ForeignKeyField' = ForeignKeyField(User, backref='clicks')  # Пользователь
    button_label: 'CharField' = CharField()  # Метка кнопки
    input_value: 'TextField' = TextField(null=True)  # Значение введенное после нажатия
    timestamp: 'DateTimeField' = DateTimeField(default=datetime.now)  # Время нажатия


class MovieSearchPreferences(BaseModel):
    """Предпочтения поиска фильмов пользователя (уникально на пользователя)"""

    user: 'ForeignKeyField' = ForeignKeyField(User, backref='search_prefs', unique=True)
    movie_title: 'CharField' = CharField(null=True)  # Название фильма
    genres: 'TextField' = TextField(null=True)  # Жанры (JSON/строка)
    result_count: 'IntegerField' = IntegerField(null=True)  # Количество результатов
    rating: 'FloatField' = FloatField(null=True)  # Минимальный рейтинг
    low_budget: 'BooleanField' = BooleanField(default=False)  # Низкий бюджет
    high_budget: 'BooleanField' = BooleanField(default=False)  # Высокий бюджет
    timestamp: 'DateTimeField' = DateTimeField(default=datetime.now)


class SearchHistory(BaseModel):
    """История поисковых запросов"""

    user: 'ForeignKeyField' = ForeignKeyField(User, backref='search_history')  # Пользователь
    result_search_: 'CharField' = CharField(null=True)  # Результат поиска (JSON/строка)
    search_date: 'DateTimeField' = DateTimeField(default=datetime.now)  # Дата поиска


def create_tables() -> None:
    """Создает все таблицы БД если они не существуют.

    Используется при инициализации бота.
    """
    with database:  # type: ignore
        database.create_tables([  # type: ignore
            User,
            UserActionLog,
            InlineButtonClick,
            MovieSearchPreferences,
            SearchHistory
        ])


def register_user_if_not_exists(
        user: 'telegram.User'  # type: ignore
) -> User:
    """Регистрирует пользователя если его нет в БД.

    Args:
        user: Объект telegram.User из update.message.from_user

    Returns:
        User: Экземпляр модели User (существующий или новый)
    """
    with database.atomic():  # type: ignore
        obj, created = User.get_or_create(
            telegram_id=user.id,
            defaults={
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            }
        )
    return obj


def log_action(
        user: Union[User, int],
        action_type: str,
        details: Optional[str] = None
) -> None:
    """Логирует действие пользователя.

    Args:
        user: User модель или telegram_id
        action_type: 'command_start', 'search_movie', 'button_click'
        details: JSON строка или текст
    """
    if isinstance(user, int):
        user_obj = User.get(telegram_id=user)
    else:
        user_obj = user

    with database.atomic():  # type: ignore
        UserActionLog.create(
            user=user_obj,
            action_type=action_type,
            details=details
        )


def log_button_click(
        user: Union[User, int],
        button_label: str,
        input_value: Optional[str] = None
) -> None:
    """Логирует нажатие inline-кнопки.

    Args:
        user: User или telegram_id
        button_label: Текст кнопки 'Фильмы 2023', 'Жанр: Ужасы'
        input_value: Ответ пользователя после callback
    """
    if isinstance(user, int):
        user_obj = User.get(telegram_id=user)
    else:
        user_obj = user

    with database.atomic():  # type: ignore
        InlineButtonClick.create(
            user=user_obj,
            button_label=button_label,
            input_value=input_value
        )


def save_search_history(
        user: Union[User, int],
        result_search_ = None
) -> None:
    """Сохраняет результат поиска в историю.

    Args:
        user: User или telegram_id
        result_search_: JSON результатов или название фильма
    """
    if isinstance(user, int):
        user_obj = User.get(telegram_id=user)
    else:
        user_obj = user

    with database.atomic():  # type: ignore
        SearchHistory.create(
            user=user_obj,
            result_search_=result_search_,
            search_date=datetime.now()
        )