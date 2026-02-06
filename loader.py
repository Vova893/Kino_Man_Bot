"""
Модуль инициализации бота с FSM-хранилищем.

Инициализация:
1. SQLite база данных (example.db)
2. TeleBot с state_storage для FSM
3. Логирование INFO уровня
4. Переменная bots_abilities для приветствия

Экспорт: bot, bots_abilities, database
"""

import logging
from telebot import TeleBot
from peewee import SqliteDatabase
from config_data.config import BOT_TOKEN
from states.states import storage  # FSM хранилище состояний

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger: logging.Logger = logging.getLogger(__name__)

#  Инициализация базы данных SQLite
database: SqliteDatabase = SqliteDatabase('example.db')

#  Создание бота с FSM хранилищем (ПЕРЕД импортом handlers!)
bot: TeleBot = TeleBot(
    token=BOT_TOKEN,
    state_storage=storage,  # Поддержка состояний FSM
    parse_mode='HTML'       # HTML по умолчанию
)

#  Текст возможностей бота (используется в /start)
bots_abilities: str = """
🎬 <b>Я бот Киноман</b> — найду для вас фильмы:

🔍 <i>Поиск по:</i>
• Названию фильма
• Жанрам (боевик, ужасы...)
• Рейтингу (6+, 7+, 8+)
• Бюджету (низкий/высокий)

📜 История ваших поисков
"""

# Экспортируемые объекты
__all__ = ['bot', 'bots_abilities', 'database']


# """
# Модуль инициализации бота с FSM-хранилищем.
# """
# import logging
# from telebot import TeleBot
# from peewee import SqliteDatabase
# from config_data.config import BOT_TOKEN
# from states.states import storage  # ✅ Импорт хранилища
#
#
# logging.basicConfig(level=logging.INFO)
# logger = logging.getLogger(__name__)
#
# # Подключаемся к базе данных
# database = SqliteDatabase('example.db')
#
#
# # ✅ Создаём бота с хранилищем состояний ПЕРЕД импортом handlers
# bot: TeleBot = TeleBot(BOT_TOKEN, state_storage=storage)
# bots_abilities: str = "🎬 Я бот Киноман, могу найти фильмы по названию, рейтингу и бюджету!"
#
# __all__ = ['bot', 'bots_abilities']
#
#
