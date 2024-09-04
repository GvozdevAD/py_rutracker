import aiohttp
import asyncio
import certifi
import ssl

from .enums import Url
from .datacls import SearchResult
from .parsing_page import ParsingPage
from .exceptions import (
    RuTrackerAuthError,
    RuTrackerException,
    RuTrackerDownloadError,
    RuTrackerRequestError

)

class AsyncRuTrackerClient:
    def __init__(
            self,
            login: str,
            password: str,
            proxy: str = None,
    ) -> None:
        """
        """
        self._login = login
        self._password = password
        self.proxy = proxy
        self.session = None
        self.parser = ParsingPage()
        self._ssl_context = ssl.create_default_context(
            cafile=certifi.where()
        )


    async def init(self)-> aiohttp.ClientSession:
        """ 
        """
        self.session = aiohttp.ClientSession()
        await self.auth()
        return self.session
    
    async def auth(self) -> None:
        """
        Аутентифицирует пользователя на сайте RuTracker.
        :param login: Логин для аутентификации.
        :param password: Пароль для аутентификации.
        :raises RuTrackerAuthError: Если статус-код ответа не 200, 
                аутентификация не удалась, или обнаружена капча.
        """
        data = {
            'login_username': self._login,
            'login_password': self._password,
            'login': 'Вход'
        }
        try:
            async with self.session.post(
                Url.AUTH.value, 
                data=data,
                proxy=self.proxy,
                ssl=self._ssl_context
            ) as response:
                text = await response.text()
                if response.status != 200:
                    raise RuTrackerAuthError(f"Ошибка аутентификации: статус-код {response.status}")
                if "cap_sid" in text:
                    raise RuTrackerAuthError(
                        "Найдена капча при аутентикации! Пройдите её в браузере и попробуйте еще раз!"
                    )
                if not self.session.cookie_jar:
                    raise RuTrackerAuthError("Не удалось выполнить аутентификацию.")
        except Exception as _ex:
            raise RuTrackerAuthError(f"Ошибка при выполнении запроса: {_ex}")


    async def search(
            self, 
            title: str, 
            page: int = 1,
            return_search_dict: bool = False
    ) -> list[SearchResult]:
         """
         
         """
         url = Url.SEARCH.value
         params = {
                "start": (page - 1) * 50,
                "nm": title,
            }
         try:
              async with self.session.get(
                  url, 
                  params=params, 
                  ssl=self._ssl_context, 
                  proxy=self.proxy
                ) as response:
                   if response.status != 200:
                        raise Exception(f"Ошибка запроса: статус-код {response.status}")
                        
                   content = await response.text()
                   results = self.parser.search(content, return_search_dict)
                
         except Exception as ex:
              raise Exception(f"Ошибка при выполнении поиска: {ex}")

         return results

    async def search_all_pages(
            self,
            title: str,
            return_search_dict: bool = False,
            max_pages: int = 10
    ) -> list[SearchResult]:
        """
        Выполняет поиск по заданному заголовку на всех страницах (до 10 страниц).

        :param title: Заголовок для поиска.
        :param return_search_dict: Флаг, указывающий, следует ли возвращать результаты в виде словарей (если True) или объектов SearchResult (если False).
        :return: Список всех результатов поиска.

        :raises RuTrackerParsingException: Если происходит ошибка при парсинге результатов поиска.
        """
        tasks = []
        for page in range(1, max_pages):
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

    async def download(self, topic_id_or_url: int | str) -> bytes:
        """
        Асинхронно получает файл торрента по указанному идентификатору или URL.

        :param topic_id_or_url: Идентификатор (топика) или URL для получения файла торрента.
        :return: Содержимое файла торрента в виде байтов.

        :raises RuTrackerRequestException: Если запрос на получение файла торрента завершился ошибкой.
        :raises RuTrackerDownloadError: Если передан недопустимый параметр.
        """
        if isinstance(topic_id_or_url, int):
            params = {"t": topic_id_or_url}
            url = Url.DOWNLOAD.value
        elif isinstance(topic_id_or_url, str) and topic_id_or_url.startswith(Url.DOWNLOAD.value):
            url = topic_id_or_url
            params = None
        else:
            raise RuTrackerDownloadError(
                "Передан недопустимый параметр. Ожидался topic_id (int) "
                "или URL (str), начинающийся с 'https://rutracker.org/forum/dl.php?t='."
            )

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
            if "filename" not in response.headers.get("Content-Disposition"):
                raise RuTrackerDownloadError("Файл с таким ID не найден")
            # if "Error" in await response.text():
            #     raise RuTrackerDownloadError("Файл с таким ID не найден")

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
