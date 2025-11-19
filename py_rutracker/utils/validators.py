from typing import Optional, Union

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
