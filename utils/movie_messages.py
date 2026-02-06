import time
import logging
from typing import List, Dict, Any, Union, Optional
from telebot.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from loader import bot
from keyboards.inline.search_menu import main_search_menu

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ГЛОБАЛЬНЫЙ КЭШ: {chat_id: List[фильмов]}
SEARCH_CACHE: Dict[int, List[Dict[str, Any]]] = {}


def get_chat_id(obj: Union[Message, CallbackQuery]) -> Optional[int]:
    """Chat ID из obj."""
    if hasattr(obj, 'chat'):
        return obj.chat.id
    if hasattr(obj, 'message') and hasattr(obj.message, 'chat'):
        return obj.message.chat.id
    return None


def movie_messages(
        messages: List[Dict[str, Any]],
        obj: Optional[Union[Message, CallbackQuery]] = None,
        chat_id: Optional[int] = None,
        page: int = 1,
        per_page: int = 6,
        save_cache: bool = True,
        edit_mode: bool = False,
        edit_message_id: Optional[int] = None,
        history_mode: bool = False
) -> None:
    """history_mode=False показывает меню, True=только фильмы без пагинации!"""
    if not messages:
        logger.warning("⚠️ Нет фильмов")
        return

    if page < 1:
        page = 1

    target_chat_id = chat_id or get_chat_id(obj)
    if not target_chat_id:
        return

    # КЭШ (только для обычных поисков)
    if save_cache and not history_mode:
        SEARCH_CACHE[target_chat_id] = messages
        logger.info(f"💾 Кэш: {len(messages)} фильмов для {target_chat_id}")

    # ПАГИНАЦИЯ (по ПАРАМ сообщений)
    total_messages = len(messages)
    total_pages = (total_messages + per_page - 1) // per_page
    page_messages = messages[(page - 1) * per_page:page * per_page]

    logger.info(f"📱 {target_chat_id}: {page}/{total_pages} ({len(page_messages)} сообщений)")

    # ОТПРАВЛЯЕМ ФИЛЬМЫ/ОПИСАНИЯ (ВСЕГДА)
    for i, msg in enumerate(page_messages):
        try:
            if msg.get('photo'):
                bot.send_photo(
                    target_chat_id,
                    msg['photo'],
                    caption=msg.get('caption', ''),
                    parse_mode=msg.get('parse_mode', 'HTML')
                )
            elif msg.get('text'):
                bot.send_message(
                    target_chat_id,
                    msg['text'],
                    parse_mode=msg.get('parse_mode', 'HTML')
                )
            time.sleep(0.34)
            logger.info(f"✅ #{i + 1}: отправлено ({page}/{total_pages})")
        except Exception as e:
            logger.error(f"❌ #{i}: {e}")

    # МЕНЮ ПАГИНАЦИИ ТОЛЬКО для обычных поисков (НЕ история!)
    if not history_mode:
        markup = InlineKeyboardMarkup(row_width=3)
        if page > 1:
            markup.add(InlineKeyboardButton("◀️ Назад", callback_data=f"page_{page - 1}_{per_page}"))
        markup.add(InlineKeyboardButton(f"{page}/{total_pages}", callback_data="nop"))
        if page < total_pages:
            markup.add(InlineKeyboardButton("▶️ Вперед", callback_data=f"page_{page + 1}_{per_page}"))
        markup.row(InlineKeyboardButton("🏠 Меню", callback_data="main_menu"))

        info_text = f"📱 <b>{page}/{total_pages}</b> ({total_messages} сообщений)"

        # РЕДАКТИРОВАНИЕ ПАНЕЛИ
        if edit_mode and edit_message_id:
            try:
                bot.edit_message_text(
                    info_text,
                    target_chat_id,
                    edit_message_id,
                    reply_markup=markup,
                    parse_mode='HTML'
                )
                logger.info(f"✅ Панель отредактирована: {page}")
            except Exception as e:
                logger.warning(f"⚠️ Edit failed: {e}")
                bot.send_message(target_chat_id, info_text, reply_markup=markup, parse_mode='HTML')
        else:
            # НОВАЯ ПАНЕЛЬ
            bot.send_message(
                target_chat_id,
                info_text,
                reply_markup=markup,
                parse_mode='HTML'
            )
            logger.info(f"✅ Новая панель: {page}")
    else:
        logger.info(f"✅ История: меню скрыто для {target_chat_id}")

    logger.info(f"✅ Полная страница {page} готова!")


@bot.callback_query_handler(func=lambda call: call.data.startswith('page_'))
def handle_pagination(call: CallbackQuery) -> None:
    """ПАГИНАЦИЯ обычных поисков."""
    bot.answer_callback_query(call.id)

    parts = call.data.split('_')
    page = int(parts[1])
    per_page = int(parts[2])
    chat_id = call.message.chat.id
    message_id = call.message.message_id

    cached_movies = SEARCH_CACHE.get(chat_id, [])
    if cached_movies:
        movie_messages(
            cached_movies,
            call,
            page=page,
            per_page=per_page,
            save_cache=False,
            edit_mode=True,
            edit_message_id=message_id,
            history_mode=False  # ✅ Обычный поиск
        )
    else:
        bot.send_message(chat_id, "🔍 Повторите поиск!")


@bot.callback_query_handler(func=lambda call: call.data == 'main_menu')
def back_to_main_menu(call: CallbackQuery) -> None:
    """Главное меню."""
    bot.answer_callback_query(call.id)
    try:
        bot.edit_message_text(
            "🎬 Выберите поиск:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=main_search_menu(),
            parse_mode='HTML'
        )
    except:
        bot.send_message(call.message.chat.id, "🎬 Выберите поиск:", reply_markup=main_search_menu())


@bot.callback_query_handler(func=lambda call: call.data == 'nop')
def nop_handler(call: CallbackQuery) -> None:
    """Пустой обработчик."""
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda call: call.data == 'pagination_info')
def pagination_info(call: CallbackQuery) -> None:
    """Индикатор страниц."""
    bot.answer_callback_query(call.id)


__all__ = ['movie_messages', 'SEARCH_CACHE']
