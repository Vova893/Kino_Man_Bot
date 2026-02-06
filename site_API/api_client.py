"""
PoiskKino.dev API клиент для Telegram-бота поиска фильмов.

Поддерживает 5 типов поиска:
1. По названию (1 фильм)
2. По жанрам из БД (user settings)
3. По рейтингу из БД (топ-10)
4. Низкий бюджет (100k-30M)
5. Высокий бюджет (30M-300M)

Форматирует результаты для movie_messages: poster + caption + описание
"""

import requests
from typing import List, Dict, Any
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config_data.config import RAPID_API_KEY
from database.database import MovieSearchPreferences, save_search_history


def create_session() -> requests.Session:
    """Создает requests.Session с retry логикой."""
    session = requests.Session()
    retry_strategy = Retry(
        total=3,  # 3 попытки
        status_forcelist=[429, 500, 502, 503, 504],  # Retry на ошибки сервера
        backoff_factor=1  # Задержка 1s, 2s, 4s
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def safe_api_request(url: str, headers: Dict[str, str], params: Dict[str, Any], timeout: int = 60) -> List[
    Dict[str, Any]]:
    """Безопасный запрос с retry и увеличенным timeout."""
    session = create_session()

    try:
        response = session.get(url, headers=headers, params=params, timeout=timeout)
        response.raise_for_status()  # Проверяем статус код
        return response.json().get('docs', [])
    except requests.exceptions.ReadTimeout:
        print(f"⏱️  Timeout {timeout}s — API слишком медленный")
        return []
    except requests.exceptions.RequestException as e:
        print(f"❌ API ошибка: {e}")
        return []


def result_conversion(user: Any, movies_data: List[Dict[str, Any]], count: int) -> List[Dict[str, Any]]:
    """Конвертирует сырые данные API в сообщения Telegram."""
    selected_films = [movie for movie in movies_data[:count] if movie.get('name')]
    messages: List[Dict[str, Any]] = []

    for movie in selected_films:
        name = movie.get('name', '—')
        poster_url = movie.get('poster', {}).get('url') or movie.get('poster', {}).get('previewUrl')
        if not poster_url:
            continue  # Пропускаем без постера
        rating_kp = movie.get('rating', {}).get('kp', '—')
        year = movie.get('year', '—')
        full_description = movie.get('description', '—')
        age_rating = movie.get('ageRating', '—')

        # Жанры
        genres = movie.get('genres', [])
        genres_list = [genre.get('name', '') for genre in genres[:2] if genre.get('name')]
        genres_text = ', '.join(genres_list) if genres_list else '—'

        # КОРОТКАЯ ПОДПИСЬ ДЛЯ ПОСТЕРА (900 символов)
        short_caption = f"""🎬 <b>{name}</b>
📅 {year} | ⭐ <b>{rating_kp}</b> | ⏰ {age_rating}+

🎭 {genres_text}"""

        # ПОЛНОЕ ОПИСАНИЕ ОТДЕЛЬНЫМ СООБЩЕНИЕМ
        full_desc_msg = {
            'text': f"<b>📖 Подробное описание:</b>\n\n{full_description}",
            'parse_mode': 'HTML'
        }

        messages.extend([
            {
                'photo': poster_url,
                'caption': short_caption,
                'parse_mode': 'HTML'
            },
            full_desc_msg  # Второе сообщение с полным описанием
        ])
    save_search_history(user, result_search_=messages)

    return messages


# ФУНКЦИИ API
def poisk_kino_api_name(name: str, user: Any) -> List[Dict[str, Any]]:
    """Поиск по названию (timeout=60s)."""
    url = "https://api.poiskkino.dev/v1.4/movie/search"
    headers = {"X-API-KEY": RAPID_API_KEY}
    params = {"name": name}

    movies_data = safe_api_request(url, headers, params, timeout=60)
    return result_conversion(user, movies_data, 1)


def poisk_kino_api(user: Any) -> List[Dict[str, Any]]:
    """Поиск по жанрам."""
    url = "https://api.poiskkino.dev/v1.4/movie"
    headers = {"X-API-KEY": RAPID_API_KEY}

    try:
        preference = MovieSearchPreferences.get(MovieSearchPreferences.user == user)
        params = {"genres.name": preference.genres.split(", ") if preference.genres else []}

        movies_data = safe_api_request(url, headers, params, timeout=60)
        return result_conversion(user, movies_data, preference.result_count or 10)
    except:
        return []


def poisk_kino_api_rating(user: Any) -> List[Dict[str, Any]]:
    """Поиск по рейтингу."""
    url = "https://api.poiskkino.dev/v1.4/movie"
    headers = {"X-API-KEY": RAPID_API_KEY}

    try:
        preference = MovieSearchPreferences.get(MovieSearchPreferences.user == user)
        params = {"rating.kp": preference.rating}

        movies_data = safe_api_request(url, headers, params, timeout=60)
        return result_conversion(user, movies_data, 100)
    except:
        return []


def poisk_kino_api_low_budget(user: Any) -> List[Dict[str, Any]]:
    """Низкий бюджет."""
    url = "https://api.poiskkino.dev/v1.4/movie"
    headers = {"X-API-KEY": RAPID_API_KEY}
    params = {"budget.value": [100000, 30000000]}

    movies_data = safe_api_request(url, headers, params, timeout=60)
    return result_conversion(user, movies_data, 100)


def poisk_kino_api_high_budget(user: Any) -> List[Dict[str, Any]]:
    """Высокий бюджет."""
    url = "https://api.poiskkino.dev/v1.4/movie"
    headers = {"X-API-KEY": RAPID_API_KEY}
    params = {"budget.value": [30000000, 300000000]}

    movies_data = safe_api_request(url, headers, params, timeout=60)
    return result_conversion(user, movies_data, 100)
