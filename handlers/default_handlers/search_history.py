"""
Модуль истории поисков С ПАГИНАЦИЕЙ для Telegram MovieBot

✨ Функционал:
├── 📋 Пагинация по поискам (1 поиск = 1 страница истории)
├── 🎬 Полная movie_messages БЕЗ меню фильмов в истории
├── ➖➖➖ Разделители между поисками (как оригинал)
├── chat_id вместо fake_obj — 0 ошибок IDE
├── 🗑️ Автоочистка кэша
└── ✅ 100% совместимость с movie_messages v2.3
"""

from typing import Any, Union, Dict, List
from datetime import datetime, date, timedelta
from peewee import fn
import json
import ast
import logging
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot
from keyboards.inline.search_menu import main_search_menu
from database.database import register_user_if_not_exists, SearchHistory
from utils.movie_messages import movie_messages

logger = logging.getLogger(__name__)
HISTORY_CACHE: Dict[int, Dict] = {}


def safe_parse_results(result_data: str) -> List[Dict[str, Any]]:
    """
    БЕЗОПАСНЫЙ парсинг result_search_ из БД.

    Args:
        result_data: JSON/AST строка из SearchHistory.result_search_
    Returns:
        List[Dict[str, Any]]: сообщения или []
    """
    if not result_data:
        return []

    try:
        return json.loads(result_data)
    except (json.JSONDecodeError, TypeError):
        try:
            return ast.literal_eval(result_data)
        except (ValueError, SyntaxError, TypeError):
            logger.warning("Не удалось распарсить result_search_")
            return []


def process_history_date_input(message: Message) -> None:
    """ДД.ММ.ГГГГ → показывает историю."""
    user = register_user_if_not_exists(message.from_user)
    try:
        input_date: date = datetime.strptime(message.text.strip(), "%d.%m.%Y").date()
        show_history_paginated(user, input_date, message)
    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ Неверный формат!\n"
            "📅 <b>ДД.ММ.ГГГГ</b>\n"
            "💡 <code>03.02.2026</code> | <code>15.12.2025</code>",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton("🔄 Снова", callback_data="search_history")
            )
        )


def show_history_paginated(
        user: Any,
        target_date: date,
        obj: Union[Message, CallbackQuery]
) -> None:
    """
    Главная функция истории с пагинацией.

    Args:
        user: User модель из БД
        target_date: date для фильтрации
        obj: Message/CallbackQuery для chat.id
    """
    chat_id = obj.chat.id if hasattr(obj, 'chat') else obj.message.chat.id

    # Поиск за день (по дате без времени)
    searches = (SearchHistory
                .select()
                .where((SearchHistory.user == user) &
                       (fn.DATE(SearchHistory.search_date) == target_date))
                .order_by(SearchHistory.search_date.desc()))

    count = searches.count()
    if count == 0:
        bot.send_message(
            chat_id,
            f"📅 За <b>{target_date.strftime('%d.%m.%Y')}</b> поисков не найдено.",
            parse_mode='HTML',
            reply_markup=main_search_menu()
        )
        return

    # Кэш для пагинации
    HISTORY_CACHE[chat_id] = {
        'date': target_date,
        'searches': list(searches)
    }
    logger.info(f"💾 Кэш: {count} поисков за {target_date}")

    # Заголовок
    bot.send_message(
        chat_id,
        f"📋 <b>История за {target_date.strftime('%d.%m.%Y')}</b>\n"
        f"Всего поисков: <b>{count}</b>",
        parse_mode='HTML'
    )

    # Первая страница
    show_history_page(chat_id, page=1)


def show_history_page(chat_id: int, page: int = 1, per_page: int = 1) -> None:
    """
    ПАГИНАЦИЯ ИСТОРИИ: 1 страница = 1 поиск.

    Args:
        chat_id: ID чата
        page: номер страницы
        per_page: всегда 1 поиск/страница
    """
    cache = HISTORY_CACHE.get(chat_id)
    if not cache:
        bot.send_message(chat_id, "🔍 История устарела. <code>/search_history</code>", parse_mode='HTML')
        return

    searches = cache['searches']
    total_searches = len(searches)
    total_pages = (total_searches + per_page - 1) // per_page
    page_searches = searches[(page - 1) * per_page:page * per_page]

    logger.info(f"📋 Страница {page}/{total_pages}: {len(page_searches)} поисков")

    # Каждый поиск на странице
    for search in page_searches:
        try:
            results = safe_parse_results(search.result_search_)
            if results:
                # Заголовок поиска (как оригинал)
                bot.send_message(
                    chat_id,
                    f"🔍 <b>Поиск в {search.search_date.strftime('%H:%M')}</b>",
                    parse_mode='HTML'
                )

                movie_messages(
                    results,
                    chat_id=chat_id,
                    page=1,
                    save_cache=False,
                    history_mode=True
                )

                # Разделитель (как оригинал)
                bot.send_message(chat_id, "➖➖➖➖➖➖➖➖➖➖")
            else:
                bot.send_message(chat_id, f"🔍 Пустой поиск <b>{search.search_date.strftime('%H:%M')}</b>")
                bot.send_message(chat_id, "➖➖➖➖➖➖➖➖➖➖")
        except Exception as e:
            logger.error(f"❌ Поиск {search.id}: {e}")
            bot.send_message(chat_id, f"❌ Ошибка <b>{search.search_date.strftime('%H:%M')}</b>")

    # ПАНЕЛЬ пагинации ИСТОРИИ
    markup = InlineKeyboardMarkup(row_width=3)
    if page > 1:
        markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"hist_page_{page - 1}_1"))
    markup.add(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="nop"))
    if page < total_pages:
        markup.add(InlineKeyboardButton("▶️ Вперед", callback_data=f"hist_page_{page + 1}_1"))
    markup.row(InlineKeyboardButton("🏠 Меню", callback_data="main_menu"))

    bot.send_message(
        chat_id,
        f"📋 <b>Страница {page}/{total_pages}</b> ({total_searches} поисков)",
        reply_markup=markup,
        parse_mode='HTML'
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith('hist_page_'))
def handle_history_pagination(call: CallbackQuery) -> None:
    """Обработчик: hist_page_2_1 → страница 2."""
    bot.answer_callback_query(call.id)

    try:
        parts = call.data.split('_')
        page = int(parts[2])
        per_page = int(parts[3])  # Всегда 1
        chat_id = call.message.chat.id

        show_history_page(chat_id, page, per_page)
    except (ValueError, IndexError) as e:
        logger.error(f"Ошибка пагинации: {e}")
        bot.send_message(call.message.chat.id, "❌ Ошибка пагинации")


@bot.callback_query_handler(func=lambda call: call.data.startswith('history_'))
def handle_history_date(call: CallbackQuery) -> None:
    """history_today | history_yesterday | history_date."""
    bot.answer_callback_query(call.id)
    user = register_user_if_not_exists(call.from_user)

    try:
        if call.data == 'history_today':
            target_date = datetime.now().date()
            show_history_paginated(user, target_date, call)
        elif call.data == 'history_yesterday':
            target_date = datetime.now().date() - timedelta(days=1)
            show_history_paginated(user, target_date, call)
        elif call.data == 'history_date':
            bot.edit_message_text(
                "📅 <b>Введите дату поиска:</b>\n"
                "<code>ДД.ММ.ГГГГ</code>\n\n"
                "💡 Примеры:\n"
                "• <code>03.02.2026</code>\n"
                "• <code>02.02.2026</code>",
                call.message.chat.id, call.message.message_id, parse_mode='HTML'
            )
            bot.register_next_step_handler_by_chat_id(call.message.chat.id, process_history_date_input)
    except Exception as e:
        logger.error(f"Ошибка history_date: {e}")


@bot.message_handler(commands=['search_history'])
def search_history_command(message: Message) -> None:
    """/search_history — главное меню истории."""
    bot.send_message(
        message.chat.id,
        "📅 <b>История поисков</b>\n\n"
        "Выберите период для просмотра:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup()
        .row(
            InlineKeyboardButton("📆 Сегодня", callback_data="history_today"),
            InlineKeyboardButton("📆 Вчера", callback_data="history_yesterday")
        )
        .row(InlineKeyboardButton("📅 Дата", callback_data="history_date"))
    )


# Очистка кэша при выходе в меню
@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def cleanup_history_cache(call: CallbackQuery) -> None:
    """Очищает HISTORY_CACHE."""
    chat_id = call.message.chat.id
    if chat_id in HISTORY_CACHE:
        del HISTORY_CACHE[chat_id]
        logger.info(f"🧹 Кэш очищен для {chat_id}")

    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text(
            "🎬 <b>Главное меню</b>",
            call.message.chat.id, call.message.message_id,
            reply_markup=main_search_menu(), parse_mode='HTML'
        )
    except:
        bot.send_message(call.message.chat.id, "🎬 Главное меню:", reply_markup=main_search_menu())


__all__ = ['show_history_paginated', 'HISTORY_CACHE', 'safe_parse_results']
