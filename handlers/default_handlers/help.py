"""
Обработчик команды /help для Telegram-бота поиска фильмов.

Показывает список доступных команд из DEFAULT_COMMANDS
в формате "/команда - описание".
"""

from telebot.types import Message
from config_data.config import DEFAULT_COMMANDS
from loader import bot


@bot.message_handler(commands=['help'])
def bot_help(message: 'Message') -> None:
    """Отображает справку по доступным командам бота.

    Формат вывода:
    /start - Запустить бота
    /help - Вывести справку

    Args:
        message: Сообщение с командой /help
    """
    # Формируем список команд: ["/start - Запустить бота"]
    commands_text: list[str] = [
        f"/<code>{command}</code> - {description}"
        for command, description in DEFAULT_COMMANDS
    ]

    help_message: str = "\n".join(commands_text)

    bot.reply_to(
        message,
        f"📋 <b>Доступные команды:</b>\n\n{help_message}",
        parse_mode='HTML'
    )

