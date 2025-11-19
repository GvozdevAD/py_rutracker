from typing import List, Optional, Union

from ..enums import Url
from ..exceptions import (
    RuTrackerAuthError,
    RuTrackerDownloadError,
    RuTrackerRequestError,
    RuTrackerValidationError,
)


def validate_topic_id_or_url(
    topic_id_or_url: Union[int, str],
) -> tuple[str, Optional[dict]]:
    """
    Валидирует и нормализует topic_id или URL для скачивания торрента.

    :param topic_id_or_url: Идентификатор топика (int) или URL (str).
    :return: Кортеж (url, params), где url - URL для запроса, params - параметры запроса.
    :raises RuTrackerDownloadError: Если передан недопустимый параметр.
    """
    if isinstance(topic_id_or_url, int):
        params = {"t": topic_id_or_url}
        url = Url.DOWNLOAD.value
        return url, params
    elif isinstance(topic_id_or_url, str) and topic_id_or_url.startswith(
        Url.DOWNLOAD.value
    ):
        url = topic_id_or_url
        params = None
        return url, params
    else:
        raise RuTrackerDownloadError(
            "Передан недопустимый параметр. Ожидался topic_id (int) "
            "или URL (str), начинающийся с 'https://rutracker.org/forum/dl.php?t='.",
            topic_id_or_url=topic_id_or_url
        )


def validate_auth_response(text: str, status_code: int, has_cookies: bool) -> None:
    """
    Валидирует ответ на запрос аутентификации.

    :param text: Текст ответа от сервера.
    :param status_code: HTTP статус-код ответа.
    :param has_cookies: Наличие cookies в ответе.
    :raises RuTrackerAuthError: Если аутентификация не удалась.
    """
    if status_code != 200:
        raise RuTrackerAuthError(
            f"Ошибка аутентификации: статус-код {status_code}",
            status_code=status_code
        )
    if "cap_sid" in text:
        raise RuTrackerAuthError(
            "Найдена капча при аутентификации! Пройдите её в браузере и попробуйте еще раз!",
            status_code=status_code
        )
    if not has_cookies:
        raise RuTrackerAuthError(
            "Не удалось выполнить аутентификацию.",
            status_code=status_code
        )


def get_auth_data(login: str, password: str) -> dict:
    """
    Формирует данные для запроса аутентификации.

    :param login: Логин пользователя.
    :param password: Пароль пользователя.
    :return: Словарь с данными для POST-запроса.
    :raises RuTrackerValidationError: Если логин или пароль не проходят валидацию.
    """
    validate_login_password(login, password)
    return {"login_username": login.strip(), "login_password": password.strip(), "login": "Вход"}


def validate_login_password(login: str, password: str) -> None:
    """
    Валидирует логин и пароль для аутентификации.

    :param login: Логин пользователя.
    :param password: Пароль пользователя.
    :raises RuTrackerValidationError: Если логин или пароль не проходят валидацию.
    """
    if not login or not isinstance(login, str):
        raise RuTrackerValidationError(
            "Логин не может быть пустым",
            field_name="login",
            field_value=login
        )
    
    login_stripped = login.strip()
    if not login_stripped:
        raise RuTrackerValidationError(
            "Логин не может быть пустым или состоять только из пробелов",
            field_name="login",
            field_value=login
        )
    
    if len(login_stripped) < 3:
        raise RuTrackerValidationError(
            "Логин должен содержать минимум 3 символа",
            field_name="login",
            field_value=login
        )
    
    if not password or not isinstance(password, str):
        raise RuTrackerValidationError(
            "Пароль не может быть пустым",
            field_name="password",
            field_value=password
        )
    
    password_stripped = password.strip()
    if not password_stripped:
        raise RuTrackerValidationError(
            "Пароль не может быть пустым или состоять только из пробелов",
            field_name="password",
            field_value=password
        )
    
    if len(password_stripped) < 3:
        raise RuTrackerValidationError(
            "Пароль должен содержать минимум 3 символа",
            field_name="password",
            field_value=password
        )


def validate_search_title(title: str) -> None:
    """
    Валидирует заголовок для поиска.

    :param title: Заголовок для поиска.
    :raises RuTrackerValidationError: Если заголовок не проходит валидацию.
    """
    if not title or not isinstance(title, str):
        raise RuTrackerValidationError(
            "Заголовок поиска не может быть пустым",
            field_name="title",
            field_value=title
        )
    
    title_stripped = title.strip()
    if not title_stripped:
        raise RuTrackerValidationError(
            "Заголовок поиска не может быть пустым или состоять только из пробелов",
            field_name="title",
            field_value=title
        )
    
    if len(title_stripped) > 200:
        raise RuTrackerValidationError(
            "Заголовок поиска не может быть длиннее 200 символов",
            field_name="title",
            field_value=title
        )


def validate_search_page(page: int) -> None:
    """
    Валидирует номер страницы для поиска.

    :param page: Номер страницы (начинается с 1).
    :raises RuTrackerValidationError: Если номер страницы не проходит валидацию.
    """
    if not isinstance(page, int):
        raise RuTrackerValidationError(
            "Номер страницы должен быть целым числом",
            field_name="page",
            field_value=page
        )
    
    if page < 1:
        raise RuTrackerValidationError(
            "Номер страницы должен быть больше 0",
            field_name="page",
            field_value=page
        )


def build_search_params(title: str, page: int, page_size: int = 50) -> dict:
    """
    Формирует параметры для запроса поиска.

    :param title: Заголовок для поиска.
    :param page: Номер страницы (начинается с 1).
    :param page_size: Размер страницы (по умолчанию 50).
    :return: Словарь с параметрами запроса.
    :raises RuTrackerValidationError: Если параметры не проходят валидацию.
    """
    validate_search_title(title)
    validate_search_page(page)
    
    return {
        "start": (page - 1) * page_size,
        "nm": title.strip(),
    }


def validate_forum_ids(forum_ids: List[int]) -> None:
    """
    Валидирует список ID форумов.

    :param forum_ids: Список ID форумов.
    :raises RuTrackerValidationError: Если список не проходит валидацию.
    """
    if not isinstance(forum_ids, list):
        raise RuTrackerValidationError(
            "forum_ids должен быть списком",
            field_name="forum_ids",
            field_value=forum_ids
        )
    
    if len(forum_ids) == 0:
        raise RuTrackerValidationError(
            "forum_ids не может быть пустым списком",
            field_name="forum_ids",
            field_value=forum_ids
        )
    
    for forum_id in forum_ids:
        if not isinstance(forum_id, int):
            raise RuTrackerValidationError(
                f"Все элементы forum_ids должны быть целыми числами, получен: {type(forum_id).__name__}",
                field_name="forum_ids",
                field_value=forum_ids
            )


def validate_sort_option(sort_option: int) -> None:
    """
    Валидирует опцию сортировки.

    :param sort_option: Значение опции сортировки.
    :raises RuTrackerValidationError: Если опция не проходит валидацию.
    """
    if not isinstance(sort_option, int):
        raise RuTrackerValidationError(
            "sort_option должен быть целым числом",
            field_name="sort_option",
            field_value=sort_option
        )
    
    if sort_option <= 0:
        raise RuTrackerValidationError(
            "sort_option должен быть больше 0",
            field_name="sort_option",
            field_value=sort_option
        )


def validate_sort_direction(sort_direction: int) -> None:
    """
    Валидирует направление сортировки.

    :param sort_direction: Направление сортировки (1 - возрастание, 2 - убывание).
    :raises RuTrackerValidationError: Если направление не проходит валидацию.
    """
    if not isinstance(sort_direction, int):
        raise RuTrackerValidationError(
            "sort_direction должен быть целым числом",
            field_name="sort_direction",
            field_value=sort_direction
        )
    
    if sort_direction not in (1, 2):
        raise RuTrackerValidationError(
            "sort_direction должен быть равен 1 (возрастание) или 2 (убывание)",
            field_name="sort_direction",
            field_value=sort_direction
        )


def validate_time_filter(time_filter: int) -> None:
    """
    Валидирует фильтр по времени.

    :param time_filter: Значение фильтра по времени.
    :raises RuTrackerValidationError: Если фильтр не проходит валидацию.
    """
    if not isinstance(time_filter, int):
        raise RuTrackerValidationError(
            "time_filter должен быть целым числом",
            field_name="time_filter",
            field_value=time_filter
        )
    
    if time_filter < 0:
        raise RuTrackerValidationError(
            "time_filter должен быть больше или равен 0",
            field_name="time_filter",
            field_value=time_filter
        )


def validate_search_id(search_id: str) -> None:
    """
    Валидирует ID поиска.

    :param search_id: ID поиска.
    :raises RuTrackerValidationError: Если ID не проходит валидацию.
    """
    if not search_id or not isinstance(search_id, str):
        raise RuTrackerValidationError(
            "search_id не может быть пустым",
            field_name="search_id",
            field_value=search_id
        )
    
    search_id_stripped = search_id.strip()
    if not search_id_stripped:
        raise RuTrackerValidationError(
            "search_id не может быть пустым или состоять только из пробелов",
            field_name="search_id",
            field_value=search_id
        )


def build_search_form_params(
    title: str,
    forum_ids: Optional[List[int]] = None,
    sort_option: Optional[int] = None,
    sort_direction: Optional[int] = None,
    time_filter: Optional[int] = None,
) -> List[tuple]:
    """
    Формирует параметры для POST запроса поиска через форму.

    :param title: Заголовок для поиска.
    :param forum_ids: Список ID форумов (по умолчанию [-1] - все имеющиеся).
    :param sort_option: Опция сортировки (опционально).
    :param sort_direction: Направление сортировки (1 - возрастание, 2 - убывание, опционально).
    :param time_filter: Фильтр по времени (опционально).
    :return: Список кортежей (key, value) для POST запроса (для использования с data=[...]).
    :raises RuTrackerValidationError: Если параметры не проходят валидацию.
    """
    validate_search_title(title)
    
    params = []
    
    if forum_ids is not None:
        validate_forum_ids(forum_ids)
        for forum_id in forum_ids:
            params.append(("f[]", forum_id))
    else:
        params.append(("f[]", -1))
    
    if sort_option is not None:
        validate_sort_option(sort_option)
        params.append(("o", sort_option))
    
    if sort_direction is not None:
        validate_sort_direction(sort_direction)
        params.append(("s", sort_direction))
    
    if time_filter is not None:
        validate_time_filter(time_filter)
        params.append(("tm", time_filter))
    
    params.append(("nm", title.strip()))
    
    params.append(("pn", ""))
    
    return params


def build_search_pagination_params(
    title: str,
    search_id: str,
    page: int,
    page_size: int = 50,
) -> dict:
    """
    Формирует параметры для GET запроса пагинации поиска.

    :param title: Заголовок для поиска.
    :param search_id: ID поиска, полученный из первого POST запроса.
    :param page: Номер страницы (начинается с 1).
    :param page_size: Размер страницы (по умолчанию 50).
    :return: Словарь с параметрами запроса.
    :raises RuTrackerValidationError: Если параметры не проходят валидацию.
    """
    validate_search_title(title)
    validate_search_id(search_id)
    validate_search_page(page)
    
    return {
        "search_id": search_id,
        "start": (page - 1) * page_size,
        "nm": title.strip(),
    }
