"""
Обработчик неизвестных текстовых сообщений (fallback handler).

Активируется когда:
- Текст получен без активного состояния FSM
- Команда не распознана системой
- Пользователь ввел произвольный текст

Показывает дружелюбное сообщение с подсказкой.
"""

from telebot.types import Message
from loader import bot


@bot.message_handler(
    content_types=['text'],
    state=None,
    func=lambda m: bot.get_state(m.from_user.id, m.chat.id) is None
)
def bot_echo(message: 'Message') -> None:
    """Fallback-обработчик неизвестных команд/текста.

    Фильтры:
    - content_types=['text'] — только текстовые сообщения
    - state=None — без активного FSM состояния
    - func=... — дополнительная проверка состояния по user+chat ID

    Args:
        message: Входящее текстовое сообщение

    Возвращает:
        Ответ с подсказкой использования /start или меню
    """
    bot.reply_to(
        message,
        f'❓ Неизвестная команда: <b>{message.text}</b>\n\n'
        f'📋 Используйте <code>/start</code> или кнопки меню',
        parse_mode='HTML'
    )

