from abc import ABC, abstractmethod
from typing import Optional, Union

from ..core.constants import DEFAULT_MAX_SEARCH_PAGES, SEARCH_PAGE_SIZE
from ..models.search import SearchResult
from ..enums import Url
from ..exceptions import RuTrackerParsingError, RuTrackerRequestError
from ..parsers.page import ParsingPage
from ..utils.validators import (
    build_search_params,
    get_auth_data,
    validate_auth_response,
    validate_topic_id_or_url,
)


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
        """
        self._login = login
        self._password = password
        self.parser = ParsingPage()

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
            raise RuTrackerParsingError(
                f"Ошибка парсинга результатов поиска: {ex}"
            )
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

    @abstractmethod
    def search(
        self,
        title: str,
        page: int = 1,
        return_search_dict: bool = False
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
    def download(self, topic_id_or_url: Union[int, str]) -> bytes:
        """
        Получает файл торрента по указанному идентификатору или URL.

        :param topic_id_or_url: Идентификатор (топика) или URL для получения файла торрента.
        :return: Содержимое файла торрента в виде байтов.
        """
        pass

