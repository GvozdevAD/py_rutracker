import asyncio
import ssl
from pathlib import Path
from typing import Optional, Union

import aiohttp
import certifi

from ..core.base import BaseRuTrackerClient
from ..core.constants import DEFAULT_USER_AGENT
from ..enums import Url
from ..exceptions import (
    RuTrackerAuthError,
    RuTrackerDownloadError,
    RuTrackerParsingError,
    RuTrackerRequestError,
)
from ..logger import get_logger
from ..models.search import SearchResult
from ..models.search_form import SearchFormData
from ..parsers.search_form import SearchFormParser
from ..utils.retry import async_retry_on_network_error

logger = get_logger(__name__)


class AsyncRuTrackerClient(BaseRuTrackerClient):
    def __init__(
        self,
        login: str,
        password: str,
        proxy: Optional[str] = None,
        user_agent: Optional[str] = None,
    ) -> None:
        """
        Инициализирует асинхронный клиент RuTracker.

        :param login: Логин для аутентификации.
        :param password: Пароль для аутентификации.
        :param proxy: URL прокси-сервера (опционально).
        :param user_agent: User-Agent для HTTP-запросов (опционально).
        """
        super().__init__(login, password)
        self.proxy = proxy
        self.user_agent = user_agent or DEFAULT_USER_AGENT
        self.session = None
        self._ssl_context = ssl.create_default_context(cafile=certifi.where())

    async def init(self) -> aiohttp.ClientSession:
        """
        Инициализирует асинхронную сессию и выполняет аутентификацию.

        :return: Объект aiohttp.ClientSession.
        """
        logger.debug("Инициализация асинхронной сессии")
        headers = {"User-Agent": self.user_agent}
        self.session = aiohttp.ClientSession(headers=headers)
        await self.auth()
        logger.info("Сессия успешно инициализирована и аутентификация выполнена")
        return self.session

    async def auth(self) -> None:
        """
        Аутентифицирует пользователя на сайте RuTracker.

        :raises RuTrackerAuthError: Если статус-код ответа не 200,
                аутентификация не удалась, или обнаружена капча.
        """
        logger.debug("Начало процесса аутентификации")
        data = self._get_auth_data()
        auth_url = Url.AUTH.value
        try:
            await self._send_auth_request(auth_url, data)
            logger.info("Аутентификация успешно выполнена")
        except RuTrackerRequestError as ex:
            logger.error(f"Ошибка аутентификации: {ex}")
            raise RuTrackerAuthError(
                f"Ошибка при выполнении запроса: {ex.message}",
                url=auth_url,
                status_code=ex.status_code
            ) from ex
    
    @async_retry_on_network_error(max_attempts=3, min_wait=2.0, max_wait=10.0)
    async def _send_auth_request(self, url: str, data: dict) -> None:
        """
        Отправляет POST-запрос для аутентификации с поддержкой retry.
        
        :param url: URL для отправки запроса.
        :param data: Данные для POST-запроса.
        :raises RuTrackerRequestError: При сетевых ошибках или ошибках запроса.
        :raises RuTrackerAuthError: При ошибках аутентификации.
        """
        try:
            async with self.session.post(
                url, data=data, proxy=self.proxy, ssl=self._ssl_context, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                text = await response.text()
                has_cookies = bool(self.session.cookie_jar)
                status_code = response.status
                self._validate_auth_response(text, status_code, has_cookies)
        except RuTrackerAuthError:
            raise
        except Exception as ex:
            ex_type_name = type(ex).__name__
            is_network_error = ('ClientError' in ex_type_name or 
                              'ClientConnectionError' in ex_type_name or 
                              'ClientTimeout' in ex_type_name)
            
            if is_network_error:
                logger.warning(f"Сетевая ошибка при выполнении запроса аутентификации: {ex}")
            else:
                logger.exception("Неожиданная ошибка при аутентификации")
            raise RuTrackerRequestError(
                f"Ошибка при выполнении запроса: {ex}",
                url=url
            ) from ex

    async def search(
        self, title: str, page: int = 1, return_search_dict: bool = False
    ) -> list[Union[SearchResult, dict]]:
        """
        Выполняет поиск по заданному заголовку и возвращает результаты.

        :param title: Заголовок для поиска.
        :param page: Номер страницы для поиска (по умолчанию 1).
        :param return_search_dict: Флаг, указывающий, следует ли возвращать результаты
                                   в виде словарей (если True) или объектов SearchResult (если False).
        :return: Список результатов поиска.
        :raises RuTrackerValidationError: Если параметры title или page не проходят валидацию.
        :raises RuTrackerRequestError: Если происходит ошибка при выполнении запроса.
        :raises RuTrackerParsingError: Если происходит ошибка при парсинге результатов поиска.
        """
        logger.debug(f"Выполнение поиска: title='{title}', page={page}")
        url = self._get_search_url()
        params = self._build_search_params(title, page)

        try:
            content = await self._send_get_request(url, params)
            results = self._parse_search_results(content, return_search_dict)
            logger.info(
                f"Поиск завершен успешно: найдено {len(results)} результатов на странице {page}"
            )
            return results
        except RuTrackerRequestError:
            raise
        except RuTrackerParsingError as ex:
            logger.error(f"Ошибка парсинга результатов поиска: {ex}")
            raise
    
    @async_retry_on_network_error(max_attempts=3, min_wait=2.0, max_wait=10.0)
    async def _send_get_request(self, url: str, params: dict = None) -> str:
        """
        Отправляет GET-запрос с поддержкой retry и возвращает текст ответа.
        
        :param url: URL для отправки запроса.
        :param params: Параметры запроса.
        :return: Текст ответа от сервера.
        :raises RuTrackerRequestError: При ошибках запроса.
        """
        try:
            async with self.session.get(
                url, params=params, ssl=self._ssl_context, proxy=self.proxy, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:
                if response.status != 200:
                    logger.warning(f"Получен неожиданный статус-код: {response.status}")
                    error = RuTrackerRequestError(
                        f"Ошибка запроса: статус-код {response.status}",
                        url=url,
                        status_code=response.status,
                        params=params
                    )
                    if 500 <= response.status < 600:
                        raise error
                    raise error

                content = await response.text()
                
                if "top-login-box" in content:
                    logger.warning("Обнаружена необходимость аутентификации")
                    raise RuTrackerRequestError(
                        "Необходима аутентификация.",
                        url=url,
                        status_code=response.status,
                        params=params
                    )
                
                return content
        except Exception as ex:
            ex_type_name = type(ex).__name__
            is_network_error = ('ClientError' in ex_type_name or 
                              'ClientConnectionError' in ex_type_name or 
                              'ClientTimeout' in ex_type_name)
            
            if is_network_error:
                logger.warning(f"Сетевая ошибка при выполнении GET-запроса: {ex}")
            else:
                logger.exception("Неожиданная ошибка при выполнении запроса")
            raise RuTrackerRequestError(
                f"Ошибка при выполнении запроса: {ex}",
                url=url,
                params=params
            ) from ex

    async def search_all_pages(
        self,
        title: str,
        return_search_dict: bool = False,
        max_pages: Optional[int] = None,
    ) -> list[Union[SearchResult, dict]]:
        """
        Выполняет поиск по заданному заголовку на всех страницах (до max_pages страниц).

        :param title: Заголовок для поиска.
        :param return_search_dict: Флаг, указывающий, следует ли возвращать результаты в виде словарей (если True) или объектов SearchResult (если False).
        :param max_pages: Максимальное количество страниц для поиска (по умолчанию используется значение из констант).
        :return: Список всех результатов поиска.

        :raises RuTrackerParsingError: Если происходит ошибка при парсинге результатов поиска.
        """
        if max_pages is None:
            max_pages = self._get_max_pages()

        logger.info(
            f"Начало поиска по всем страницам: title='{title}', max_pages={max_pages}"
        )
        tasks = []
        for page in range(1, max_pages + 1):
            tasks.append(self.search(title, page, return_search_dict))
        results = await asyncio.gather(*tasks, return_exceptions=True)
        all_results = []
        for i, result in enumerate(results, 1):
            if isinstance(result, Exception):
                logger.warning(f"Ошибка при поиске на странице {i}: {result}")
                continue
            if result:
                all_results.extend(result)
        logger.info(
            f"Поиск по всем страницам завершен: найдено {len(all_results)} результатов"
        )
        return all_results

    async def get_torrent(self, topic_id_or_url: Union[int, str]) -> bytes:
        """
        Асинхронно получает содержимое файла торрента по указанному идентификатору или URL.

        :param topic_id_or_url: Идентификатор (топика) или URL для получения файла торрента.
        :return: Содержимое файла торрента в виде байтов.

        :raises RuTrackerRequestError: Если запрос на получение файла торрента завершился ошибкой.
        :raises RuTrackerDownloadError: Если передан недопустимый параметр или файл не найден.
        """
        logger.debug(f"Начало получения торрента: topic_id_or_url={topic_id_or_url}")
        url, params = self._validate_download_params(topic_id_or_url)

        try:
            content = await self._send_get_request_for_download(url, params, topic_id_or_url)
            logger.info(f"Торрент успешно получен: размер {len(content)} байт")
            return content
        except (RuTrackerRequestError, RuTrackerDownloadError):
            raise
    
    @async_retry_on_network_error(max_attempts=3, min_wait=2.0, max_wait=10.0)
    async def _send_get_request_for_download(self, url: str, params: dict = None, topic_id_or_url: Union[int, str] = None) -> bytes:
        """
        Отправляет GET-запрос для скачивания торрента с поддержкой retry.
        
        :param url: URL для отправки запроса.
        :param params: Параметры запроса.
        :param topic_id_or_url: Идентификатор топика или URL (для контекста ошибок).
        :return: Содержимое файла в виде байтов.
        :raises RuTrackerRequestError: При ошибках запроса.
        :raises RuTrackerDownloadError: При ошибках скачивания.
        """
        try:
            async with self.session.get(
                url, params=params, ssl=self._ssl_context, proxy=self.proxy, timeout=aiohttp.ClientTimeout(total=30)
            ) as response:

                if response.status != 200:
                    logger.warning(
                        f"Ошибка при получении торрента: статус-код {response.status}"
                    )
                    error = RuTrackerRequestError(
                        f"Ошибка при получении файла: {response.status}",
                        url=url,
                        status_code=response.status,
                        params=params
                    )
                    if 500 <= response.status < 600:
                        raise error
                    raise error

                content = await response.read()
                content_disposition = response.headers.get("Content-Disposition", "")
                if "filename" not in content_disposition:
                    logger.error(
                        "Файл не найден: отсутствует заголовок Content-Disposition"
                    )
                    raise RuTrackerDownloadError(
                        "Файл с таким ID не найден",
                        topic_id_or_url=topic_id_or_url,
                        url=url,
                        status_code=response.status
                    )

                return content
        except (RuTrackerDownloadError, RuTrackerRequestError):
            raise
        except Exception as ex:
            ex_type_name = type(ex).__name__
            is_network_error = ('ClientError' in ex_type_name or 
                              'ClientConnectionError' in ex_type_name or 
                              'ClientTimeout' in ex_type_name)
            
            if is_network_error:
                logger.warning(f"Сетевая ошибка при получении торрента: {ex}")
            else:
                logger.exception("Неожиданная ошибка при получении торрента")
            raise RuTrackerRequestError(
                f"Ошибка при получении торрента: {ex}",
                url=url,
                params=params
            ) from ex

    async def download(
        self,
        topic_id_or_url: Union[int, str],
        save_path: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> str:
        """
        Асинхронно скачивает файл торрента и сохраняет его на диск.

        :param topic_id_or_url: Идентификатор (топика) или URL для получения файла торрента.
        :param save_path: Путь к директории для сохранения файла. Если None, используется текущая директория.
        :param filename: Имя файла. Если None, используется topic_id.torrent.
        :return: Полный путь к сохраненному файлу.
        :raises RuTrackerRequestError: Если запрос на получение файла торрента завершился ошибкой.
        :raises RuTrackerDownloadError: Если передан недопустимый параметр или файл не найден.
        """
        content = await self.get_torrent(topic_id_or_url)
        file_path = self._prepare_download_path(topic_id_or_url, save_path, filename)

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Торрент успешно сохранен: {file_path}")
        return str(file_path)

    async def get_search_form(self, force_refresh: bool = False) -> SearchFormData:
        """
        Асинхронно получает данные формы поиска RuTracker.

        :param force_refresh: Принудительно обновить кеш, игнорируя время жизни.
        :return: Объект SearchFormData с данными формы поиска.
        :raises RuTrackerRequestError: Если запрос на получение формы завершился ошибкой.
        :raises RuTrackerParsingError: Если произошла ошибка при парсинге формы.
        """
        if self.session is None or self.session.closed:
            raise RuTrackerRequestError(
                "Сессия не инициализирована. Используйте await client.init() или async with client.",
                url=f"{Url.FORUM.value}/tracker.php"
            )

        if not force_refresh and self._is_search_form_cache_valid():
            cached_data = self._get_search_form_cache()
            if cached_data:
                logger.debug("Получение формы поиска из кеша")
                return cached_data

        logger.debug("Запрос формы поиска с сервера")

        url = f"{Url.FORUM.value}/tracker.php"
        try:
            text = await self._send_get_request(url, params=None)
        except RuTrackerRequestError:
            raise


        try:
            parser = SearchFormParser()
            form_data = parser.parse(text)
            logger.info("Форма поиска успешно распарсена")
        except Exception as ex:
            logger.exception("Ошибка при парсинге формы поиска")
            html_snippet = text[:200] if text else None
            raise RuTrackerParsingError(
                f"Ошибка парсинга формы поиска: {ex}",
                html_snippet=html_snippet
            ) from ex

        self._set_search_form_cache(form_data)

        return form_data

    async def close(self):
        """
        Закрытие сессии
        """
        if self.session and not self.session.closed:
            logger.debug("Закрытие асинхронной сессии")
            await self.session.close()
            self.session = None
            logger.info("Сессия успешно закрыта")

    async def __aenter__(self):
        """
        Асинхронная инициализация, вызываемая при входе в контекстный менеджер.
        """
        await self.init()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Асинхронное закрытие сессии при выходе из контекста.
        """
        await self.close()
        if exc_type:
            logger.error(
                f"Произошла ошибка в контекстном менеджере: {exc_value}",
                exc_info=(exc_type, exc_value, traceback),
            )
        return False
