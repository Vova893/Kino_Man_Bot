from telebot.states import State, StatesGroup
from telebot.storage import StateMemoryStorage

"""
Определение состояний FSM и хранилище.
"""
# Создаём хранилище состояний
storage = StateMemoryStorage()


# Определяем состояния
class States(StatesGroup):
    """Группа состояний для поиска фильмов."""

    waiting_params: State = State()     # Ожидание параметров
    waiting_genres: State = State()     # Выбор жанров (множественное)
    waiting_count: State = State()      # Выбор количества
    waiting_query: State = State()      # Ввод запроса по имени

