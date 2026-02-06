"""
Стартовые обработчики команд для Telegram-бота поиска фильмов.

Содержит:
- /start — приветствие + главное меню
- Общий текст — навигация по кнопкам
- Проверку состояния поиска (FSM-like)
"""


from telebot.types import Message
from loader import *
from keyboards.reply.reply_button import repli_button
from keyboards.inline.search_menu import main_search_menu
from database.database import register_user_if_not_exists, log_action
from handlers.default_handlers.search_history import search_history_command


@bot.message_handler(commands=['start'])
def bot_start(message: 'Message') -> None:
    """Инициализация сессии пользователя и главное приветствие.

    Действия:
    1. Регистрация пользователя в БД
    2. Логирование запуска /start
    3. Отправка персонализированного приветствия
    4. Reply клавиатура с основными функциями

    Args:
        message: Сообщение с командой /start
    """
    user = register_user_if_not_exists(message.from_user)
    log_action(user, 'command_start', details='Пользователь запустил бота')

    markup = repli_button()
    bot.send_message(
        message.chat.id,
        f"🎬 Привет, <b>{message.from_user.full_name}</b>!\n\n"
        f"{bots_abilities}",
        parse_mode='HTML',
        reply_markup=markup
    )


def _is_search_waiting(message: 'Message') -> bool:
    """Проверяет активное ожидание ввода для поиска.

    Использует telebot storage (retrieve_data) для FSM-подобной логики.

    Args:
        message: Входящее сообщение

    Returns:
        bool: True если bot ждет ввода (movie_title, date и т.д.)
    """
    try:
        user_id: int = message.from_user.id
        chat_id: int = message.chat.id
        with bot.retrieve_data(user_id, chat_id) as data:  # type: ignore
            waiting: bool = bool(data.get('waiting_for'))
            return waiting
    except Exception as e:
        print(f"🔍 [CHECK] Нет данных FSM → FALSE: {e}")
        return False


@bot.message_handler(
    content_types=['text'],
    func=lambda msg: not _is_search_waiting(msg)
)
def handle_text(message: 'Message') -> None:
    """Общий обработчик текста ВНЕ режима поиска.

    Распознает команды из reply клавиатуры:
    - 🔍 Поиск фильмов → main_search_menu()
    - 📜 История → search_history_command()

    Args:
        message: Текстовое сообщение (не в состоянии поиска)
    """
    text: str = message.text.lower().strip()

    # 🔍 Поиск фильмов
    if text in ['🔍 поиск фильмов', 'поиск фильмов']:
        bot.send_message(
            message.chat.id,
            '🎥 <b>Выберите тип поиска:</b>',
            parse_mode='HTML',
            reply_markup=main_search_menu()
        )
        log_action(register_user_if_not_exists(message.from_user), 'search_menu')

    # 📜 История поисков
    elif text in ['📜 история', 'история поиска', 'history']:
        search_history_command(message)

    # Перезапуск
    elif text == 'start':
        bot.send_message(
            message.chat.id,
            '🎬 Для начала используйте <code>/start</code>',
            parse_mode='HTML',
            reply_markup=repli_button()
        )

