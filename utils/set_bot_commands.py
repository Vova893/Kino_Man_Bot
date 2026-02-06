"""
Настройка встроенных команд бота в меню Telegram.

Регистрирует команды /start, /help в красивом меню под полем ввода.
"""

from telebot import TeleBot
from telebot.types import BotCommand
from config_data.config import DEFAULT_COMMANDS


def set_default_commands(bot: 'TeleBot') -> None:
    """Регистрирует команды бота в меню Telegram (под полем ввода).

    Формат BotCommand(command, description):
    - command: имя команды без слеша ('start', 'help')
    - description: видимое описание для пользователей

    Args:
        bot: экземпляр TeleBot (из loader.bot)

    Использует DEFAULT_COMMANDS:
    DEFAULT_COMMANDS = (
        ('start', 'Запустить бота'),
        ('help', 'Вывести справку')
    )

    Результат в Telegram:
    /start - Запустить бота
    /help - Вывести справку
    """
    bot.set_my_commands(
        [BotCommand(command, description) for command, description in DEFAULT_COMMANDS]
    )

