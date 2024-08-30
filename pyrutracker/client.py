import requests

from .datacls import SearchResult
from .enums import Url
from .exceptions import (
    RuTrackerAuthException, 
    RuTrackerRequestException, 
    RuTrackerParsingException
)
from .parsing_page import ParsingPage


class RuTrackerClient:
    def __init__(
            self,
            login: str,
            password: str,
            proxy: dict = {"http":"", "https":""}
    ) -> None:
        """
        Инициализирует клиент RuTracker.

        :param login: Логин для аутентификации.
        :param password: Пароль для аутентификации.
        :param proxy: Словарь с прокси-серверами для HTTP и HTTPS.
        """
        self.session = self._init_session(proxy)
        self.auth(login, password)
        self.parser = ParsingPage()

    def _init_session(
            self, 
            proxy: dict[str,str]
    ) -> requests.Session:
        """
        Инициализирует сессию requests с заданными прокси.

        :param proxy: Словарь с прокси-серверами для HTTP и HTTPS.
        :return: Объект requests.Session с обновленными прокси.
        """
        session = requests.session()
        session.proxies.update(proxy)
        return session

    def _send_request(
            self, 
            url: str, 
            params: dict
    ) -> requests.Response:
        """
        Отправляет GET-запрос на указанный URL с параметрами.

        :param url: URL для отправки запроса.
        :param params: Параметры запроса.
        :return: Объект requests.Response с ответом от сервера.
        :raises RuTrackerRequestException: Если статус-код ответа не 200 или содержимое страницы указывает на необходимость аутентификации.
        """
        response = self.session.get(url, params=params)
        if response.status_code != 200:
            raise RuTrackerRequestException(f"Ошибка запроса: статус-код {response.status_code}")
        if "top-login-box" in response.text:
            raise RuTrackerRequestException("Необходима аутентификация.")
        return response

    def auth(
            self, 
            login: str, 
            password: str
    ) -> None:
        """
        Аутентифицирует пользователя на сайте RuTracker.

        :param login: Логин для аутентификации.
        :param password: Пароль для аутентификации.
        :raises RuTrackerAuthException: Если статус-код ответа не 200, 
                аутентификация не удалась, или обнаружена капча.
        """
        data = {
            'login_username': login,
            'login_password': password,
            'login': 'Вход'
        }
        try:
            response = self.session.post(
                Url.AUTH.value, 
                data=data
            )
            if response.status_code != 200:
                raise RuTrackerAuthException(
                    f"Ошибка аутентификации: статус-код {response.status_code}"
                )
            if "cap_sid" in response.text:
                raise RuTrackerAuthException(
                    "Найдена капча при аутентификацию! Пройдите ее в браузере и попробуйте еще раз!"
                )
            if not self.session.cookies:
                raise RuTrackerAuthException(
                    "Не удалось выполнить аутентификацию."
                )
        except Exception as _ex:
            raise RuTrackerAuthException(
                f"Ошибка при выполнении запроса: {_ex}"
            )
    
    def search(
            self, 
            title: str, 
            page: int = 1,
            return_search_dict: bool = False
    ) -> list[SearchResult | dict]:
        """
        Выполняет поиск по заданному заголовку и возвращает результаты.

        :param title: Заголовок для поиска.
        :param page: Номер страницы для поиска (по умолчанию 1).
        :param return_search_dict: Флаг, указывающий, следует ли возвращать результаты в виде словарей (если True) или объектов SearchResult (если False).
        :return: Список результатов поиска.
        :raises RuTrackerParsingException: Если происходит ошибка при парсинге результатов поиска.
        """
        url = Url.SEARCH.value
        params = {
            "start": (page-1)*50,
            "nm": title,
        }
        response = self._send_request(url, params)
        try:
            results = self.parser.search(response.text, return_search_dict)
        except Exception as _ex:
            raise RuTrackerParsingException(f"Ошибка парсинга результатов поиска: {_ex}")
        return results

    def search_all_pages(
            self, 
            title: str,
            return_search_dict: bool = False
    ) -> list[SearchResult | dict]:
        """
        Выполняет поиск по заданному заголовку на всех страницах (до 10 страниц).

        :param title: Заголовок для поиска.
        :param return_search_dict: Флаг, указывающий, следует ли возвращать результаты в виде словарей (если True) или объектов SearchResult (если False).
        :return: Список всех результатов поиска.

        :raises RuTrackerParsingException: Если происходит ошибка при парсинге результатов поиска.
        """
        all_results = []
        page = 1
        while page <= 10:
            results = self.search(title, page, return_search_dict)
            if not results:
                break
            all_results.extend(results)
            page += 1
        
        return all_results

    def get_torrent_file(
            self, 
            topic_id: int
    ) -> bytes:
        """
        Получает файл торрента по указанному идентификатору темы.

        :param topic_id: Идентификатор темы (топика) для получения файла торрента.
        :return: Содержимое файла торрента в виде байтов.

        :raises RuTrackerRequestException: Если запрос на получение файла торрента завершился ошибкой.
        """
        params = {
            "t": topic_id
        }
        response = self._send_request(
            Url.DOWNLOAD.value,
            params
        )
        return response.content

