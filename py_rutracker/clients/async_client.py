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
        try:
            async with self.session.post(
                Url.AUTH.value, data=data, proxy=self.proxy, ssl=self._ssl_context
            ) as response:
                text = await response.text()
                has_cookies = bool(self.session.cookie_jar)
                self._validate_auth_response(text, response.status, has_cookies)
                logger.info("Аутентификация успешно выполнена")
        except RuTrackerAuthError as ex:
            logger.error(f"Ошибка аутентификации: {ex}")
            raise
        except Exception as ex:
            logger.exception("Неожиданная ошибка при аутентификации")
            raise RuTrackerAuthError(f"Ошибка при выполнении запроса: {ex}") from ex

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
        :raises RuTrackerRequestError: Если происходит ошибка при выполнении запроса.
        :raises RuTrackerParsingError: Если происходит ошибка при парсинге результатов поиска.
        """
        logger.debug(f"Выполнение поиска: title='{title}', page={page}")
        url = self._get_search_url()
        params = self._build_search_params(title, page)

        try:
            async with self.session.get(
                url, params=params, ssl=self._ssl_context, proxy=self.proxy
            ) as response:
                if response.status != 200:
                    logger.warning(f"Получен неожиданный статус-код: {response.status}")
                    raise RuTrackerRequestError(
                        f"Ошибка запроса: статус-код {response.status}"
                    )

                content = await response.text()
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
        except Exception as ex:
            logger.exception("Неожиданная ошибка при выполнении поиска")
            raise RuTrackerRequestError(f"Ошибка при выполнении поиска: {ex}") from ex

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
            async with self.session.get(
                url, params=params, ssl=self._ssl_context, proxy=self.proxy
            ) as response:

                if response.status != 200:
                    logger.warning(
                        f"Ошибка при получении торрента: статус-код {response.status}"
                    )
                    raise RuTrackerRequestError(
                        f"Ошибка при получении файла: {response.status}"
                    )

                content = await response.read()
                content_disposition = response.headers.get("Content-Disposition", "")
                if "filename" not in content_disposition:
                    logger.error(
                        "Файл не найден: отсутствует заголовок Content-Disposition"
                    )
                    raise RuTrackerDownloadError("Файл с таким ID не найден")

                logger.info(f"Торрент успешно получен: размер {len(content)} байт")
                return content
        except (RuTrackerRequestError, RuTrackerDownloadError):
            raise
        except Exception as ex:
            logger.exception("Неожиданная ошибка при получении торрента")
            raise RuTrackerRequestError(f"Ошибка при получении торрента: {ex}") from ex

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
                "Сессия не инициализирована. Используйте await client.init() или async with client."
            )

        if not force_refresh and self._is_search_form_cache_valid():
            cached_data = self._get_search_form_cache()
            if cached_data:
                logger.debug("Получение формы поиска из кеша")
                return cached_data

        logger.debug("Запрос формы поиска с сервера")

        url = f"{Url.FORUM.value}/tracker.php"
        try:
            async with self.session.get(
                url, ssl=self._ssl_context, proxy=self.proxy
            ) as response:
                if response.status != 200:
                    logger.warning(f"Получен неожиданный статус-код: {response.status}")
                    raise RuTrackerRequestError(
                        f"Ошибка запроса: статус-код {response.status}"
                    )

                text = await response.text()

                if "top-login-box" in text:
                    logger.warning("Обнаружена необходимость аутентификации")
                    raise RuTrackerRequestError("Необходима аутентификация.")
        except RuTrackerRequestError:
            raise
        except Exception as ex:
            logger.exception("Неожиданная ошибка при запросе формы поиска")
            raise RuTrackerRequestError(
                f"Ошибка при получении формы поиска: {ex}"
            ) from ex

        try:
            parser = SearchFormParser()
            form_data = parser.parse(text)
            logger.info("Форма поиска успешно распарсена")
        except Exception as ex:
            logger.exception("Ошибка при парсинге формы поиска")
            raise RuTrackerParsingError(f"Ошибка парсинга формы поиска: {ex}") from ex

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
