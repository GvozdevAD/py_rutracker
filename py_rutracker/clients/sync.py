from typing import List, Optional, Union

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
from ..utils.retry import retry_on_network_error

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
        self._search_id_cache: dict = {}
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

    @retry_on_network_error(max_attempts=3, min_wait=2.0, max_wait=10.0)
    def _send_request(self, url: str, params: dict = None) -> requests.Response:
        """
        Отправляет GET-запрос на указанный URL с параметрами.
        Автоматически повторяет запрос при сетевых ошибках и временных ошибках сервера (5xx).

        :param url: URL для отправки запроса.
        :param params: Параметры запроса.
        :return: Объект requests.Response с ответом от сервера.
        :raises RuTrackerRequestError: Если статус-код ответа не 200 или содержимое
        страницы указывает на необходимость аутентификации.
        """
        logger.debug(f"Отправка GET-запроса: url={url}, params={params}")
        try:
            response = self.session.get(url, params=params, timeout=30)
        except Exception as ex:
            ex_type_name = type(ex).__name__
            is_network_error = ('ConnectionError' in ex_type_name or 
                              'Timeout' in ex_type_name or 
                              'RequestException' in ex_type_name)
            
            if is_network_error:
                logger.warning(f"Сетевая ошибка при выполнении HTTP-запроса: {ex}")
            else:
                logger.exception("Неожиданная ошибка при выполнении HTTP-запроса")
            raise RuTrackerRequestError(
                f"Ошибка при выполнении запроса: {ex}",
                url=url,
                params=params
            ) from ex
        
        if response.status_code != 200:
            logger.warning(f"Получен неожиданный статус-код: {response.status_code}")
            error = RuTrackerRequestError(
                f"Ошибка запроса: статус-код {response.status_code}",
                url=url,
                status_code=response.status_code,
                params=params
            )
            if 500 <= response.status_code < 600:
                raise error
            raise error
        
        if "top-login-box" in response.text:
            logger.warning("Обнаружена необходимость аутентификации")
            raise RuTrackerRequestError(
                "Необходима аутентификация.",
                url=url,
                status_code=response.status_code,
                params=params
            )
        return response

    def auth(self, login: str, password: str) -> None:
        """
        Аутентифицирует пользователя на сайте RuTracker.

        :param login: Логин для аутентификации.
        :param password: Пароль для аутентификации.
        :raises RuTrackerValidationError: Если логин или пароль не проходят валидацию.
        :raises RuTrackerAuthError: Если статус-код ответа не 200,
                аутентификация не удалась, или обнаружена капча.
        """
        logger.debug("Начало процесса аутентификации")
        data = self._get_auth_data()
        auth_url = Url.AUTH.value
        try:
            response = self._send_auth_request(auth_url, data)
            self._validate_auth_response(
                response.text, response.status_code, bool(self.session.cookies)
            )
            logger.info("Аутентификация успешно выполнена")
        except RuTrackerRequestError as ex:
            logger.error(f"Ошибка аутентификации: {ex}")
            raise RuTrackerAuthError(
                f"Ошибка при выполнении запроса: {ex.message}",
                url=auth_url,
                status_code=ex.status_code
            ) from ex
        except RuTrackerAuthError as ex:
            logger.error(f"Ошибка аутентификации: {ex}")
            if not hasattr(ex, 'url') or ex.url is None:
                ex.url = auth_url
            raise
    
    @retry_on_network_error(max_attempts=3, min_wait=2.0, max_wait=10.0)
    def _send_post_request(self, url: str, data: list) -> requests.Response:
        """
        Отправляет POST-запрос с поддержкой retry.
        
        :param url: URL для отправки запроса.
        :param data: Данные для POST-запроса в виде списка кортежей (key, value).
        :return: Объект requests.Response с ответом от сервера.
        :raises RuTrackerRequestError: При сетевых ошибках или ошибках запроса.
        """
        logger.debug(f"Отправка POST-запроса: url={url}, data={data}")
        try:
            response = self.session.post(url, data=data, timeout=30)
        except Exception as ex:
            ex_type_name = type(ex).__name__
            is_network_error = ('ConnectionError' in ex_type_name or 
                              'Timeout' in ex_type_name or 
                              'RequestException' in ex_type_name)
            
            if is_network_error:
                logger.warning(f"Сетевая ошибка при выполнении POST-запроса: {ex}")
            else:
                logger.exception("Неожиданная ошибка при выполнении POST-запроса")
            raise RuTrackerRequestError(
                f"Ошибка при выполнении запроса: {ex}",
                url=url
            ) from ex
        
        if response.status_code != 200:
            logger.warning(f"Получен неожиданный статус-код: {response.status_code}")
            error = RuTrackerRequestError(
                f"Ошибка запроса: статус-код {response.status_code}",
                url=url,
                status_code=response.status_code
            )
            if 500 <= response.status_code < 600:
                raise error
            raise error
        
        if "top-login-box" in response.text:
            logger.warning("Обнаружена необходимость аутентификации")
            raise RuTrackerRequestError(
                "Необходима аутентификация.",
                url=url,
                status_code=response.status_code
            )
        return response
    
    @retry_on_network_error(max_attempts=3, min_wait=2.0, max_wait=10.0)
    def _send_auth_request(self, url: str, data: dict) -> requests.Response:
        """
        Отправляет POST-запрос для аутентификации с поддержкой retry.
        
        :param url: URL для отправки запроса.
        :param data: Данные для POST-запроса.
        :return: Объект requests.Response с ответом от сервера.
        :raises RuTrackerRequestError: При сетевых ошибках или ошибках запроса.
        """
        try:
            response = self.session.post(url, data=data, timeout=30)
            return response
        except Exception as ex:
            ex_type_name = type(ex).__name__
            is_network_error = ('ConnectionError' in ex_type_name or 
                              'Timeout' in ex_type_name or 
                              'RequestException' in ex_type_name)
            
            if is_network_error:
                logger.warning(f"Сетевая ошибка при выполнении запроса аутентификации: {ex}")
            else:
                logger.exception("Неожиданная ошибка при выполнении запроса аутентификации")
            raise RuTrackerRequestError(
                f"Ошибка при выполнении запроса: {ex}",
                url=url
            ) from ex

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
        :raises RuTrackerValidationError: Если параметры title или page не проходят валидацию.
        :raises RuTrackerRequestError: Если происходит ошибка при выполнении запроса.
        :raises RuTrackerParsingError: Если происходит ошибка при парсинге результатов поиска.
        """
        logger.debug(f"Выполнение поиска: title='{title}', page={page}")
        url = self._get_search_url()
        params = self._build_search_params(title, page)

        try:
            response = self._send_request(url, params)
        except RuTrackerRequestError as ex:
            if not hasattr(ex, 'url') or ex.url is None:
                ex.url = url
            if not hasattr(ex, 'params') or ex.params is None:
                ex.params = params
            raise

        try:
            results = self._parse_search_results(response.text, return_search_dict)
            logger.info(
                f"Поиск завершен успешно: найдено {len(results)} результатов на странице {page}"
            )
            return results
        except RuTrackerParsingError as ex:
            logger.error(f"Ошибка парсинга результатов поиска: {ex}")
            if not hasattr(ex, 'html_snippet') or ex.html_snippet is None:
                html_snippet = response.text[:200] if response.text else None
                if html_snippet:
                    ex.html_snippet = html_snippet
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
                raise RuTrackerDownloadError(
                    "Файл с таким ID не найден",
                    topic_id_or_url=topic_id_or_url,
                    url=url,
                    status_code=response.status_code
                )

            logger.info(f"Торрент успешно получен: размер {len(response.content)} байт")
            return response.content
        except (RuTrackerRequestError, RuTrackerDownloadError):
            raise
        except Exception as ex:
            logger.exception("Неожиданная ошибка при получении торрента")
            raise RuTrackerRequestError(
                f"Ошибка при получении торрента: {ex}",
                url=url,
                params=params
            ) from ex

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
    
    def search_with_form(
        self,
        title: str,
        page: int = 1,
        return_search_dict: bool = False,
        forum_ids: Optional[List[int]] = None,
        sort_option: Optional[int] = None,
        sort_direction: Optional[int] = None,
        time_filter: Optional[int] = None,
    ) -> list[Union[SearchResult, dict]]:
        """
        Выполняет поиск через форму с параметрами сортировки и фильтрации.
        Использует POST запрос для первой страницы и GET запрос с search_id для последующих страниц.
        
        :param title: Заголовок для поиска.
        :param page: Номер страницы для поиска (по умолчанию 1).
        :param return_search_dict: Флаг, указывающий, следует ли возвращать результаты
                                   в виде словарей (если True) или объектов SearchResult (если False).
        :param forum_ids: Список ID форумов (по умолчанию [-1] - все имеющиеся).
        :param sort_option: Опция сортировки (если не указана, используется из формы).
        :param sort_direction: Направление сортировки (1 - возрастание, 2 - убывание, если не указано, используется из формы).
        :param time_filter: Фильтр по времени (опционально).
        :return: Список результатов поиска.
        :raises RuTrackerValidationError: Если параметры не проходят валидацию.
        :raises RuTrackerRequestError: Если происходит ошибка при выполнении запроса.
        :raises RuTrackerParsingError: Если происходит ошибка при парсинге результатов поиска.
        """
        logger.debug(
            f"Выполнение поиска через форму: title='{title}', page={page}, "
            f"forum_ids={forum_ids}, sort_option={sort_option}, "
            f"sort_direction={sort_direction}, time_filter={time_filter}"
        )
        
        search_key = (
            title,
            tuple(sorted(forum_ids)) if forum_ids else None,
            sort_option,
            sort_direction,
            time_filter,
        )
        
        url = self._get_search_url()
        
        if page == 1:
            data = self._build_search_form_params(
                title=title,
                forum_ids=forum_ids,
                sort_option=sort_option,
                sort_direction=sort_direction,
                time_filter=time_filter,
            )
            
            try:
                response = self._send_post_request(url, data)
            except RuTrackerRequestError as ex:
                if not hasattr(ex, 'url') or ex.url is None:
                    ex.url = url
                raise
            
            try:
                results = self._parse_search_results(response.text, return_search_dict)
                
                search_id = self._extract_search_id(response.text)
                if search_id:
                    self._search_id_cache[search_key] = search_id
                    logger.debug(f"search_id сохранен в кеш: {search_id}")
                else:
                    logger.debug(f"search_id не найден на странице {page} (возможно, результаты помещаются на одну страницу)")
                
                logger.info(
                    f"Поиск через форму завершен успешно: найдено {len(results)} результатов на странице {page}"
                )
                return results
            except RuTrackerParsingError as ex:
                logger.error(f"Ошибка парсинга результатов поиска: {ex}")
                if not hasattr(ex, 'html_snippet') or ex.html_snippet is None:
                    html_snippet = response.text[:200] if response.text else None
                    if html_snippet:
                        ex.html_snippet = html_snippet
                raise
        else:
            search_id = self._search_id_cache.get(search_key)
            
            if not search_id:
                logger.debug("search_id отсутствует, выполняем POST запрос для первой страницы")
                data = self._build_search_form_params(
                    title=title,
                    forum_ids=forum_ids,
                    sort_option=sort_option,
                    sort_direction=sort_direction,
                    time_filter=time_filter,
                )
                
                try:
                    response = self._send_post_request(url, data)
                except RuTrackerRequestError as ex:
                    if not hasattr(ex, 'url') or ex.url is None:
                        ex.url = url
                    raise
                
                search_id = self._extract_search_id(response.text)
                if search_id:
                    self._search_id_cache[search_key] = search_id
                    logger.debug(f"search_id сохранен в кеш: {search_id}")
                else:
                    raise RuTrackerRequestError(
                        "Не удалось извлечь search_id из ответа для пагинации",
                        url=url
                    )
            
            params = self._build_search_pagination_params(
                title=title,
                search_id=search_id,
                page=page,
            )
            
            try:
                response = self._send_request(url, params)
            except RuTrackerRequestError as ex:
                if not hasattr(ex, 'url') or ex.url is None:
                    ex.url = url
                if not hasattr(ex, 'params') or ex.params is None:
                    ex.params = params
                raise
            
            try:
                results = self._parse_search_results(response.text, return_search_dict)
                logger.info(
                    f"Поиск через форму завершен успешно: найдено {len(results)} результатов на странице {page}"
                )
                return results
            except RuTrackerParsingError as ex:
                logger.error(f"Ошибка парсинга результатов поиска: {ex}")
                if not hasattr(ex, 'html_snippet') or ex.html_snippet is None:
                    html_snippet = response.text[:200] if response.text else None
                    if html_snippet:
                        ex.html_snippet = html_snippet
                raise
    
    def search_all_pages_with_form(
        self,
        title: str,
        return_search_dict: bool = False,
        max_pages: Optional[int] = None,
        forum_ids: Optional[List[int]] = None,
        sort_option: Optional[int] = None,
        sort_direction: Optional[int] = None,
        time_filter: Optional[int] = None,
    ) -> list[Union[SearchResult, dict]]:
        """
        Выполняет поиск через форму по заданному заголовку на всех страницах (до max_pages страниц).
        Автоматически использует POST для первой страницы и GET с search_id для остальных.
        
        :param title: Заголовок для поиска.
        :param return_search_dict: Флаг, указывающий, следует ли возвращать результаты в виде словарей (если True) или объектов SearchResult (если False).
        :param max_pages: Максимальное количество страниц для поиска (по умолчанию используется значение из констант).
        :param forum_ids: Список ID форумов (по умолчанию [-1] - все имеющиеся).
        :param sort_option: Опция сортировки (если не указана, используется из формы).
        :param sort_direction: Направление сортировки (1 - возрастание, 2 - убывание, если не указано, используется из формы).
        :param time_filter: Фильтр по времени (опционально).
        :return: Список всех результатов поиска.
        :raises RuTrackerParsingError: Если происходит ошибка при парсинге результатов поиска.
        """
        if max_pages is None:
            max_pages = self._get_max_pages()

        logger.info(
            f"Начало поиска через форму по всем страницам: title='{title}', max_pages={max_pages}, "
            f"forum_ids={forum_ids}, sort_option={sort_option}, "
            f"sort_direction={sort_direction}, time_filter={time_filter}"
        )
        all_results = []
        page = 1
        while page <= max_pages:
            try:
                results = self.search_with_form(
                    title=title,
                    page=page,
                    return_search_dict=return_search_dict,
                    forum_ids=forum_ids,
                    sort_option=sort_option,
                    sort_direction=sort_direction,
                    time_filter=time_filter,
                )
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
            f"Поиск через форму по всем страницам завершен: найдено {len(all_results)} результатов"
        )
        return all_results

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
                f"Ошибка при получении формы поиска: {ex}",
                url=url
            ) from ex

        try:
            parser = SearchFormParser()
            form_data = parser.parse(response.text)
            logger.info("Форма поиска успешно распарсена")
        except Exception as ex:
            logger.exception("Ошибка при парсинге формы поиска")
            html_snippet = response.text[:200] if response.text else None
            raise RuTrackerParsingError(
                f"Ошибка парсинга формы поиска: {ex}",
                html_snippet=html_snippet
            ) from ex

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
