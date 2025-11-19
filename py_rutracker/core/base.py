import re
from abc import ABC, abstractmethod
from pathlib import Path
from time import time
from typing import List, Optional, Union

from ..core.constants import DEFAULT_MAX_SEARCH_PAGES, SEARCH_PAGE_SIZE
from ..enums import Url
from ..exceptions import (
    RuTrackerParsingError,
)
from ..models.search import SearchResult
from ..models.search_form import SearchFormData
from ..logger import get_logger
from ..parsers.page import ParsingPage
from ..parsers.search_form import SearchFormParser
from ..utils.validators import (
    build_search_params,
    build_search_form_params,
    build_search_pagination_params,
    get_auth_data,
    validate_auth_response,
    validate_login_password,
    validate_topic_id_or_url,
)

logger = get_logger(__name__)


class BaseRuTrackerClient(ABC):
    """
    Базовый абстрактный класс для клиентов RuTracker.
    Содержит общую логику, которая используется в синхронном и асинхронном клиентах.
    """

    def __init__(self, login: str, password: str):
        """
        Инициализирует базовый клиент.

        :param login: Логин для аутентификации.
        :param password: Пароль для аутентификации.
        :raises RuTrackerValidationError: Если логин или пароль не проходят валидацию.
        """
        validate_login_password(login, password)
        self._login = login.strip()
        self._password = password.strip()
        self.parser = ParsingPage()
        self._search_form_cache: Optional[dict] = None
        self._search_form_cache_ttl: int = 86400  # 24 часа

    def _get_auth_data(self) -> dict:
        """
        Получает данные для аутентификации.

        :return: Словарь с данными для POST-запроса.
        """
        return get_auth_data(self._login, self._password)

    def _validate_auth_response(
        self, text: str, status_code: int, has_cookies: bool
    ) -> None:
        """
        Валидирует ответ на запрос аутентификации.

        :param text: Текст ответа от сервера.
        :param status_code: HTTP статус-код ответа.
        :param has_cookies: Наличие cookies в ответе.
        :raises RuTrackerAuthError: Если аутентификация не удалась.
        """
        validate_auth_response(text, status_code, has_cookies)

    def _build_search_params(self, title: str, page: int) -> dict:
        """
        Формирует параметры для запроса поиска.

        :param title: Заголовок для поиска.
        :param page: Номер страницы (начинается с 1).
        :return: Словарь с параметрами запроса.
        """
        return build_search_params(title, page, SEARCH_PAGE_SIZE)

    def _parse_search_results(
        self, html_content: str, return_search_dict: bool = False
    ) -> list[Union[SearchResult, dict]]:
        """
        Парсит HTML-контент и возвращает результаты поиска.

        :param html_content: HTML-контент страницы с результатами поиска.
        :param return_search_dict: Флаг, указывающий, следует ли возвращать результаты
                                   в виде словарей (если True) или объектов SearchResult (если False).
        :return: Список результатов поиска.
        :raises RuTrackerParsingError: Если происходит ошибка при парсинге результатов поиска.
        """
        try:
            results = self.parser.search(html_content, return_search_dict)
        except Exception as ex:
            html_snippet = html_content[:200] if html_content else None
            raise RuTrackerParsingError(
                f"Ошибка парсинга результатов поиска: {ex}",
                html_snippet=html_snippet
            ) from ex
        return results

    def _validate_download_params(
        self, topic_id_or_url: Union[int, str]
    ) -> tuple[str, Optional[dict]]:
        """
        Валидирует и нормализует параметры для скачивания торрента.

        :param topic_id_or_url: Идентификатор топика (int) или URL (str).
        :return: Кортеж (url, params), где url - URL для запроса, params - параметры запроса.
        :raises RuTrackerDownloadError: Если передан недопустимый параметр.
        """
        return validate_topic_id_or_url(topic_id_or_url)

    def _get_search_url(self) -> str:
        """
        Возвращает URL для поиска.

        :return: URL для поиска.
        """
        return Url.SEARCH.value

    def _get_download_url(self) -> str:
        """
        Возвращает базовый URL для скачивания торрентов.

        :return: URL для скачивания торрентов.
        """
        return Url.DOWNLOAD.value

    def _get_max_pages(self) -> int:
        """
        Возвращает максимальное количество страниц для поиска.

        :return: Максимальное количество страниц.
        """
        return DEFAULT_MAX_SEARCH_PAGES

    def _extract_topic_id_from_url(
        self, topic_id_or_url: Union[int, str]
    ) -> Optional[int]:
        """
        Извлекает topic_id из URL или возвращает его, если передан int.

        :param topic_id_or_url: Идентификатор топика (int) или URL (str).
        :return: Идентификатор топика или None, если не удалось извлечь.
        """
        if isinstance(topic_id_or_url, int):
            return topic_id_or_url

        try:
            # Формат URL: https://rutracker.org/forum/dl.php?t=12345
            match = re.search(r"t=(\d+)", str(topic_id_or_url))
            if match:
                return int(match.group(1))
        except Exception:
            pass

        return None

    @abstractmethod
    def search(
        self, title: str, page: int = 1, return_search_dict: bool = False
    ) -> list[Union[SearchResult, dict]]:
        """
        Выполняет поиск по заданному заголовку и возвращает результаты.

        :param title: Заголовок для поиска.
        :param page: Номер страницы для поиска (по умолчанию 1).
        :param return_search_dict: Флаг, указывающий, следует ли возвращать результаты
                                   в виде словарей (если True) или объектов SearchResult (если False).
        :return: Список результатов поиска.
        """
        pass

    @abstractmethod
    def get_torrent(self, topic_id_or_url: Union[int, str]) -> bytes:
        """
        Получает содержимое файла торрента по указанному идентификатору или URL.

        :param topic_id_or_url: Идентификатор (топика) или URL для получения файла торрента.
        :return: Содержимое файла торрента в виде байтов.
        """
        pass

    def _prepare_download_path(
        self,
        topic_id_or_url: Union[int, str],
        save_path: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> Path:
        """
        Подготавливает путь для сохранения файла торрента.

        :param topic_id_or_url: Идентификатор (топика) или URL для получения файла торрента.
        :param save_path: Путь к директории для сохранения файла. Если None, используется текущая директория.
        :param filename: Имя файла. Если None, используется topic_id.torrent.
        :return: Полный путь к файлу для сохранения.
        """
        if save_path is None:
            save_path = Path.cwd()
        else:
            save_path = Path(save_path)

        save_path.mkdir(parents=True, exist_ok=True)

        if filename is None:
            topic_id = self._extract_topic_id_from_url(topic_id_or_url)
            if topic_id is not None:
                filename = f"{topic_id}.torrent"
            else:
                filename = "torrent.torrent"
        elif not filename.endswith(".torrent"):
            filename = f"{filename}.torrent"

        return save_path / filename

    @abstractmethod
    def download(
        self,
        topic_id_or_url: Union[int, str],
        save_path: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> str:
        """
        Скачивает файл торрента и сохраняет его на диск.

        :param topic_id_or_url: Идентификатор (топика) или URL для получения файла торрента.
        :param save_path: Путь к директории для сохранения файла. Если None, используется текущая директория.
        :param filename: Имя файла. Если None, используется topic_id.torrent.
        :return: Полный путь к сохраненному файлу.
        :raises RuTrackerRequestError: Если запрос на получение файла торрента завершился ошибкой.
        :raises RuTrackerDownloadError: Если передан недопустимый параметр или файл не найден.
        """
        pass

    def _is_search_form_cache_valid(self) -> bool:
        """
        Проверяет валидность кеша формы поиска.

        :return: True если кеш существует и не истек, False в противном случае.
        """
        if self._search_form_cache is None:
            return False

        cache_timestamp = self._search_form_cache.get("timestamp", 0)
        cache_ttl = self._search_form_cache.get("ttl", self._search_form_cache_ttl)
        current_time = time()

        return (current_time - cache_timestamp) < cache_ttl

    def _get_search_form_cache(self) -> Optional[SearchFormData]:
        """
        Получает данные формы поиска из кеша, если кеш валиден.

        :return: Объект SearchFormData или None, если кеш невалиден или отсутствует.
        """
        if not self._is_search_form_cache_valid():
            return None

        return self._search_form_cache.get("data")

    def _set_search_form_cache(self, data: SearchFormData) -> None:
        """
        Сохраняет данные формы поиска в кеш.

        :param data: Объект SearchFormData для сохранения в кеш.
        """
        self._search_form_cache = {
            "data": data,
            "timestamp": time(),
            "ttl": self._search_form_cache_ttl,
        }

    def _clear_search_form_cache(self) -> None:
        """
        Очищает кеш формы поиска.
        """
        self._search_form_cache = None

    @abstractmethod
    def get_search_form(self, force_refresh: bool = False) -> SearchFormData:
        """
        Получает данные формы поиска RuTracker.

        :param force_refresh: Принудительно обновить кеш, игнорируя время жизни.
        :return: Объект SearchFormData с данными формы поиска.
        :raises RuTrackerRequestError: Если запрос на получение формы завершился ошибкой.
        :raises RuTrackerParsingError: Если произошла ошибка при парсинге формы.
        """
        pass
    
    def _get_default_sort_option(self) -> Optional[int]:
        """
        Получает выбранную опцию сортировки из SearchFormData.
        
        :return: Значение опции сортировки или None, если форма не загружена.
        """
        form_data = self._get_search_form_cache()
        if form_data and form_data.sort_options:
            for option in form_data.sort_options:
                if option.is_selected:
                    return option.value
            if form_data.sort_options:
                return form_data.sort_options[0].value
        return None
    
    def _get_default_sort_direction(self) -> Optional[int]:
        """
        Получает выбранное направление сортировки из SearchFormData.
        
        :return: Значение направления сортировки (1 или 2) или None, если форма не загружена.
        """
        form_data = self._get_search_form_cache()
        if form_data and form_data.sort_directions:
            for direction in form_data.sort_directions:
                if direction.is_selected:
                    return direction.value
            if form_data.sort_directions:
                for direction in form_data.sort_directions:
                    if direction.value == 2:
                        return 2
                return form_data.sort_directions[0].value
        return None
    
    def _extract_search_id(self, html_content: str) -> Optional[str]:
        """
        Извлекает search_id из HTML контента.
        
        :param html_content: HTML контент страницы с результатами поиска.
        :return: search_id или None, если не найден.
        """
        return self.parser.extract_search_id(html_content)
    
    def _build_search_form_params(
        self,
        title: str,
        forum_ids: Optional[List[int]] = None,
        sort_option: Optional[int] = None,
        sort_direction: Optional[int] = None,
        time_filter: Optional[int] = None,
    ) -> List[tuple]:
        """
        Формирует параметры для POST запроса поиска через форму.
        Использует значения по умолчанию из SearchFormData, если параметры не указаны.
        
        :param title: Заголовок для поиска.
        :param forum_ids: Список ID форумов (по умолчанию [-1] - все имеющиеся).
        :param sort_option: Опция сортировки (если не указана, используется из формы).
        :param sort_direction: Направление сортировки (если не указано, используется из формы).
        :param time_filter: Фильтр по времени (опционально).
        :return: Список кортежей (key, value) для POST запроса.
        """
        if sort_option is None:
            sort_option = self._get_default_sort_option()
        
        if sort_direction is None:
            sort_direction = self._get_default_sort_direction()
        
        return build_search_form_params(
            title=title,
            forum_ids=forum_ids,
            sort_option=sort_option,
            sort_direction=sort_direction,
            time_filter=time_filter,
        )
    
    def _build_search_pagination_params(
        self,
        title: str,
        search_id: str,
        page: int,
    ) -> dict:
        """
        Формирует параметры для GET запроса пагинации поиска.
        
        :param title: Заголовок для поиска.
        :param search_id: ID поиска, полученный из первого POST запроса.
        :param page: Номер страницы (начинается с 1).
        :return: Словарь с параметрами запроса.
        """
        return build_search_pagination_params(
            title=title,
            search_id=search_id,
            page=page,
            page_size=SEARCH_PAGE_SIZE,
        )
