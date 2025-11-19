import aiohttp
import asyncio
import certifi
import ssl
from typing import Optional, Union

from ..core.base import BaseRuTrackerClient
from ..core.constants import DEFAULT_USER_AGENT
from ..models.search import SearchResult
from ..enums import Url
from ..exceptions import (
    RuTrackerAuthError,
    RuTrackerDownloadError,
    RuTrackerParsingError,
    RuTrackerRequestError
)


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
        self._ssl_context = ssl.create_default_context(
            cafile=certifi.where()
        )


    async def init(self) -> aiohttp.ClientSession:
        """
        Инициализирует асинхронную сессию и выполняет аутентификацию.

        :return: Объект aiohttp.ClientSession.
        """
        headers = {
            'User-Agent': self.user_agent
        }
        self.session = aiohttp.ClientSession(headers=headers)
        await self.auth()
        return self.session
    
    async def auth(self) -> None:
        """
        Аутентифицирует пользователя на сайте RuTracker.

        :raises RuTrackerAuthError: Если статус-код ответа не 200, 
                аутентификация не удалась, или обнаружена капча.
        """
        data = self._get_auth_data()
        try:
            async with self.session.post(
                Url.AUTH.value, 
                data=data,
                proxy=self.proxy,
                ssl=self._ssl_context
            ) as response:
                text = await response.text()
                has_cookies = bool(self.session.cookie_jar)
                self._validate_auth_response(text, response.status, has_cookies)
        except RuTrackerAuthError:
            raise
        except Exception as ex:
            raise RuTrackerAuthError(
                f"Ошибка при выполнении запроса: {ex}"
            ) from ex


    async def search(
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
        :raises RuTrackerRequestError: Если происходит ошибка при выполнении запроса.
        :raises RuTrackerParsingError: Если происходит ошибка при парсинге результатов поиска.
        """
        url = self._get_search_url()
        params = self._build_search_params(title, page)
        
        try:
            async with self.session.get(
                url, 
                params=params, 
                ssl=self._ssl_context, 
                proxy=self.proxy
            ) as response:
                if response.status != 200:
                    raise RuTrackerRequestError(
                        f"Ошибка запроса: статус-код {response.status}"
                    )
                
                content = await response.text()
                return self._parse_search_results(content, return_search_dict)
        except RuTrackerRequestError:
            raise
        except RuTrackerParsingError:
            raise
        except Exception as ex:
            raise RuTrackerRequestError(
                f"Ошибка при выполнении поиска: {ex}"
            ) from ex

    async def search_all_pages(
            self,
            title: str,
            return_search_dict: bool = False,
            max_pages: Optional[int] = None
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
        
        tasks = []
        for page in range(1, max_pages + 1):
            tasks.append(
                self.search(
                    title, 
                    page, 
                    return_search_dict
                )
            )
        results = await asyncio.gather(*tasks)
        all_results = []
        for result in results:
            if result:
                all_results.extend(result)
        return all_results

    async def download(self, topic_id_or_url: Union[int, str]) -> bytes:
        """
        Асинхронно получает файл торрента по указанному идентификатору или URL.

        :param topic_id_or_url: Идентификатор (топика) или URL для получения файла торрента.
        :return: Содержимое файла торрента в виде байтов.

        :raises RuTrackerRequestError: Если запрос на получение файла торрента завершился ошибкой.
        :raises RuTrackerDownloadError: Если передан недопустимый параметр или файл не найден.
        """
        url, params = self._validate_download_params(topic_id_or_url)

        async with self.session.get(
            url, 
            params=params, 
            ssl=self._ssl_context, 
            proxy=self.proxy
        ) as response:
            
            if response.status != 200:
                raise RuTrackerRequestError(
                    f"Ошибка при получении файла: {response.status}"
                )

            content = await response.read()
            content_disposition = response.headers.get("Content-Disposition", "")
            if "filename" not in content_disposition:
                raise RuTrackerDownloadError("Файл с таким ID не найден")

        return content


    async def close(self):
        """
        Закрытие сессии
        """
        if self.session:
            await self.session.close()
    
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
            print(f"Произошла ошибка: {exc_value}")
        return False

