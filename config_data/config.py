"""
Модуль инициализации конфигурации Telegram-бота.

Загружает переменные окружения из .env:
- BOT_TOKEN: str - Токен бота от @BotFather
- RAPID_API_KEY: str - Ключ для RapidAPI (фильмы/аниме)

Стандартные команды:
- /start - Запуск бота
- /help - Справка

Зависимости:
- python-dotenv
- os (стандартная)

Файл .env должен содержать:
BOT_TOKEN=your_bot_token_here
RAPID_API_KEY=your_rapidapi_key_here

Добавьте .env в .gitignore!
"""
import os  # type: ignore
from dotenv import find_dotenv, load_dotenv  # type: ignore


if not find_dotenv():
    exit('Переменные окружения не загружены, т.к. отсутствует файл .env')  # type: ignore
load_dotenv()

BOT_TOKEN: str = os.getenv('BOT_TOKEN')  # type: ignore
RAPID_API_KEY: str = os.getenv('RAPID_API_KEY')  # type: ignore

DEFAULT_COMMANDS: tuple[tuple[str, str], ...] = (
    ('start', 'Запустить бота'),
    ('help', 'Вывести справку'),
)
