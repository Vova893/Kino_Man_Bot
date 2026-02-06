"""
Точка входа (entry point) Telegram-бота поиска фильмов.

Порядок запуска:
1. Создание таблиц БД (Peewee)
2. Регистрация команд меню (/start, /help)
3. Запуск polling с пропуском старых обновлений

Запуск: python main.py
"""

from loader import bot
import handlers  # Регистрация всех обработчиков (@bot.message_handler)
from utils.set_bot_commands import set_default_commands
from database.database import create_tables


def main() -> None:
    """Главная функция запуска бота."""
    print("🚀 Инициализация Telegram-бота 'Киноман'...")

    # 1.  Создание таблиц БД (если не существуют)
    print("  📊 Создание таблиц БД...")
    create_tables()
    print("  ✅ База данных готова")

    # 2.  Регистрация команд в меню Telegram
    print("  📱 Настройка команд меню...")
    set_default_commands(bot)
    print("  ✅ Команды зарегистрированы")

    print("🚀 Бот полностью готов к работе!")
    print("📡 Запуск polling...")

    # 3.  Запуск бота (infinity polling)
    bot.infinity_polling(
        skip_pending=True,  # Пропуск старых сообщений при перезапуске
    )


if __name__ == '__main__':
    main()

# from loader import bot
# import handlers
# from utils.set_bot_commands import set_default_commands
# from database.database import create_tables
#
#
# if __name__ == '__main__':
#     print("🚀 Запуск бота...")
#     create_tables()
#     set_default_commands(bot)
#     print("🚀 Бот готов!")
#     bot.infinity_polling(skip_pending=True)
