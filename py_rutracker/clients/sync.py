from typing import Optional, Union

import requests

from ..core.base import BaseRuTrackerClient
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


class RuTrackerClient(BaseRuTrackerClient):
    def __init__(
        self, login: str, password: str, proxies: Optional[dict] = None
    ) -> None:
        """
        Инициализирует клиент RuTracker.

        :param login: Логин для аутентификации.
        :param password: Пароль для аутентификации.
        :param proxies: Словарь с прокси-серверами для HTTP и HTTPS.
        """
        super().__init__(login, password)
        logger.debug("Инициализация синхронного клиента RuTracker")
        self.session = self._init_session(proxies)
        self.auth(login, password)
        logger.info(
            "Синхронный клиент успешно инициализирован и аутентификация выполнена"
        )

    def _init_session(self, proxies: Optional[dict]) -> requests.Session:
        """
        Инициализирует сессию requests с заданными прокси.

        :param proxies: Словарь с прокси-серверами для HTTP и HTTPS.
        :return: Объект requests.Session с обновленными прокси.
        """
        session = requests.session()
        if proxies:
            session.proxies.update(proxies)
        return session

    def _send_request(self, url: str, params: dict = None) -> requests.Response:
        """
        Отправляет GET-запрос на указанный URL с параметрами.

        :param url: URL для отправки запроса.
        :param params: Параметры запроса.
        :return: Объект requests.Response с ответом от сервера.
        :raises RuTrackerAuthError: Если статус-код ответа не 200 или содержимое
        страницы указывает на необходимость аутентификации.
        """
        logger.debug(f"Отправка GET-запроса: url={url}, params={params}")
        try:
            response = self.session.get(url, params=params)
        except Exception as ex:
            logger.exception("Ошибка при выполнении HTTP-запроса")
            raise RuTrackerAuthError(f"Ошибка при выполнении запроса: {ex}") from ex
        if response.status_code != 200:
            logger.warning(f"Получен неожиданный статус-код: {response.status_code}")
            raise RuTrackerRequestError(
                f"Ошибка запроса: статус-код {response.status_code}"
            )
        if "top-login-box" in response.text:
            logger.warning("Обнаружена необходимость аутентификации")
            raise RuTrackerRequestError("Необходима аутентификация.")
        return response

    def auth(self, login: str, password: str) -> None:
        """
        Аутентифицирует пользователя на сайте RuTracker.

        :param login: Логин для аутентификации.
        :param password: Пароль для аутентификации.
        :raises RuTrackerAuthError: Если статус-код ответа не 200,
                аутентификация не удалась, или обнаружена капча.
        """
        logger.debug("Начало процесса аутентификации")
        data = self._get_auth_data()
        try:
            response = self.session.post(
                Url.AUTH.value,
                data=data,
            )
        except Exception as ex:
            logger.exception("Неожиданная ошибка при выполнении запроса аутентификации")
            raise RuTrackerAuthError(f"Ошибка при выполнении запроса: {ex}") from ex

        try:
            self._validate_auth_response(
                response.text, response.status_code, bool(self.session.cookies)
            )
            logger.info("Аутентификация успешно выполнена")
        except RuTrackerAuthError as ex:
            logger.error(f"Ошибка аутентификации: {ex}")
            raise

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
        :raises RuTrackerRequestError: Если происходит ошибка при выполнении запроса.
        :raises RuTrackerParsingError: Если происходит ошибка при парсинге результатов поиска.
        """
        logger.debug(f"Выполнение поиска: title='{title}', page={page}")
        url = self._get_search_url()
        params = self._build_search_params(title, page)

        try:
            response = self._send_request(url, params)
        except RuTrackerRequestError as ex:
            raise RuTrackerRequestError(str(ex)) from ex

        try:
            results = self._parse_search_results(response.text, return_search_dict)
            logger.info(
                f"Поиск завершен успешно: найдено {len(results)} результатов на странице {page}"
            )
            return results
        except RuTrackerParsingError as ex:
            logger.error(f"Ошибка парсинга результатов поиска: {ex}")
            raise

    def search_all_pages(
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
        all_results = []
        page = 1
        while page <= max_pages:
            try:
                results = self.search(title, page, return_search_dict)
                if not results:
                    logger.debug(
                        f"На странице {page} результатов не найдено, завершение поиска"
                    )
                    break
                all_results.extend(results)
                page += 1
            except Exception as ex:
                logger.warning(f"Ошибка при поиске на странице {page}: {ex}")
                break

        logger.info(
            f"Поиск по всем страницам завершен: найдено {len(all_results)} результатов"
        )
        return all_results

    def get_torrent(self, topic_id_or_url: Union[int, str]) -> bytes:
        """
        Получает содержимое файла торрента по указанному идентификатору или URL.

        :param topic_id_or_url: Идентификатор (топика) или URL для получения файла торрента.
        :return: Содержимое файла торрента в виде байтов.

        :raises RuTrackerRequestError: Если запрос на получение файла торрента завершился ошибкой.
        :raises RuTrackerDownloadError: Если передан недопустимый параметр или файл не найден.
        """
        logger.debug(f"Начало получения торрента: topic_id_or_url={topic_id_or_url}")
        url, params = self._validate_download_params(topic_id_or_url)

        try:
            response = self._send_request(url, params)

            if "Error" in response.text:
                logger.error("Файл не найден: в ответе обнаружена ошибка")
                raise RuTrackerDownloadError("Файл с таким ID не найден")

            logger.info(f"Торрент успешно получен: размер {len(response.content)} байт")
            return response.content
        except (RuTrackerRequestError, RuTrackerDownloadError):
            raise
        except Exception as ex:
            logger.exception("Неожиданная ошибка при получении торрента")
            raise RuTrackerRequestError(f"Ошибка при получении торрента: {ex}") from ex

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
        content = self.get_torrent(topic_id_or_url)
        file_path = self._prepare_download_path(topic_id_or_url, save_path, filename)

        with open(file_path, "wb") as f:
            f.write(content)

        logger.info(f"Торрент успешно сохранен: {file_path}")
        return str(file_path)

    def get_search_form(self, force_refresh: bool = False) -> SearchFormData:
        """
        Получает данные формы поиска RuTracker.

        :param force_refresh: Принудительно обновить кеш, игнорируя время жизни.
        :return: Объект SearchFormData с данными формы поиска.
        :raises RuTrackerRequestError: Если запрос на получение формы завершился ошибкой.
        :raises RuTrackerParsingError: Если произошла ошибка при парсинге формы.
        """
        if not force_refresh and self._is_search_form_cache_valid():
            cached_data = self._get_search_form_cache()
            if cached_data:
                logger.debug("Получение формы поиска из кеша")
                return cached_data

        logger.debug("Запрос формы поиска с сервера")

        url = f"{Url.FORUM.value}/tracker.php"
        try:
            response = self._send_request(url, params=None)
        except RuTrackerRequestError:
            raise
        except Exception as ex:
            logger.exception("Неожиданная ошибка при запросе формы поиска")
            raise RuTrackerRequestError(
                f"Ошибка при получении формы поиска: {ex}"
            ) from ex

        try:
            parser = SearchFormParser()
            form_data = parser.parse(response.text)
            logger.info("Форма поиска успешно распарсена")
        except Exception as ex:
            logger.exception("Ошибка при парсинге формы поиска")
            raise RuTrackerParsingError(f"Ошибка парсинга формы поиска: {ex}") from ex

        self._set_search_form_cache(form_data)

        return form_data

    def __enter__(self):
        """
        Метод, вызываемый при входе в контекст менеджера ресурсов.
        """
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Метод, вызываемый при выходе из контекста менеджера ресурсов.
        """
        logger.debug("Закрытие синхронной сессии")
        self.session.close()
        if exc_type is not None:
            logger.error(
                f"Произошла ошибка в контекстном менеджере: {exc_value}",
                exc_info=(exc_type, exc_value, traceback),
            )
        logger.info("Сессия успешно закрыта")
        return False
