import requests

from .datacls import SearchResult
from .enums import Url
from .exceptions import (
    RuTrackerAuthError, 
    RuTrackerDownloadError,
    RuTrackerParsingError,
    RuTrackerRequestError, 
)
from .parsing_page import ParsingPage


class RuTrackerClient:
    def __init__(
            self,
            login: str,
            password: str,
            proxies: dict = None
    ) -> None:
        """
        Инициализирует клиент RuTracker.

        :param login: Логин для аутентификации.
        :param password: Пароль для аутентификации.
        :param proxies: Словарь с прокси-серверами для HTTP и HTTPS.
        """
        self.session = self._init_session(proxies)
        self.auth(login, password)
        self.parser = ParsingPage()

    def _init_session(
            self, 
            proxies: dict[str,str]
    ) -> requests.Session:
        """
        Инициализирует сессию requests с заданными прокси.

        :param proxies: Словарь с прокси-серверами для HTTP и HTTPS.
        :return: Объект requests.Session с обновленными прокси.
        """
        session = requests.session()
        if proxies:
            session.proxies.update(proxies)
        return session

    def _send_request(
            self, 
            url: str, 
            params: dict = None
    ) -> requests.Response:
        """
        Отправляет GET-запрос на указанный URL с параметрами.

        :param url: URL для отправки запроса.
        :param params: Параметры запроса.
        :return: Объект requests.Response с ответом от сервера.
        :raises RuTrackerAuthError: Если статус-код ответа не 200 или содержимое 
        страницы указывает на необходимость аутентификации.
        """
        try:
            response = self.session.get(url, params=params)
        except Exception as _ex:
            raise RuTrackerAuthError(
                f"Ошибка при выполнении запроса: {_ex}"
            )
        if response.status_code != 200:
            raise RuTrackerRequestError(
                f"Ошибка запроса: статус-код {response.status_code}"
            )
        if "top-login-box" in response.text:
            raise RuTrackerRequestError("Необходима аутентификация.")
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
        :raises RuTrackerAuthError: Если статус-код ответа не 200, 
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
                data=data,
            )
        except Exception as _ex:
            raise RuTrackerAuthError(
                f"Ошибка при выполнении запроса: {_ex}"
            )
        if response.status_code != 200:
            raise RuTrackerAuthError(
                f"Ошибка аутентификации: статус-код {response.status_code}"
            )
        if "cap_sid" in response.text:
            raise RuTrackerAuthError(
                "Найдена капча при аутентификацию!"\
                " Пройдите ее в браузере и попробуйте еще раз!"
            )
        if not self.session.cookies:
            raise RuTrackerAuthError(
                "Не удалось выполнить аутентификацию."
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
        :param return_search_dict: Флаг, указывающий, следует ли возвращать результаты
        в виде словарей (если True) или объектов SearchResult (если False).
        :return: Список результатов поиска.
        :raises RuTrackerParsingError: Если происходит ошибка при парсинге результатов поиска.
        """
        url = Url.SEARCH.value
        params = {
            "start": (page-1)*50,
            "nm": title,
        }
        try:
            response = self._send_request(url, params)
        except RuTrackerRequestError as _ex:
            raise RuTrackerRequestError(_ex)
        
        try:
            results = self.parser.search(response.text, return_search_dict)
        except Exception as _ex:
            raise RuTrackerParsingError(f"Ошибка парсинга результатов поиска: {_ex}")
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

    def download(
            self, 
            topic_id_or_url: int | str
    ) -> bytes:
        """
        Получает файл торрента по указанному идентификатору или URL.

        :param topic_id_or_url: Идентификатор (топика) или URL для получения файла торрента.
        :return: Содержимое файла торрента в виде байтов.

        :raises RuTrackerRequestException: Если запрос на получение файла торрента завершился ошибкой.
        :raises RuTrackerDownloadError: Если передан недопустимый параметр.
        """
        if isinstance(topic_id_or_url, int):
            params = {
                "t": topic_id_or_url
            }

            response = self._send_request(
                Url.DOWNLOAD.value,
                params
            )

        elif (isinstance(topic_id_or_url, str) and 
              topic_id_or_url.startswith(Url.DOWNLOAD.value)
        ):
            response = self._send_request(topic_id_or_url)

        else:
            raise RuTrackerDownloadError(
                "Передан недопустимый параметр. Ожидался topic_id (int)" \
                " или URL (str), начинающийся с" \
                " 'https://rutracker.org/forum/dl.php?t='."
            )

        if "Error" in response.text:
            raise RuTrackerDownloadError("Файл с таким ID не найден")
        
        return response.content

    def get_torrent_file(self, ):
        """ """

    def __enter__(self):
        """
        Метод, вызываемый при входе в контекст менеджера ресурсов.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Метод, вызываемый при выходе из контекста менеджера ресурсов.
        """
        
        self.session.close()
        if exc_type is not None:
            print(f"Произошла ошибка: {exc_value}")
        return False