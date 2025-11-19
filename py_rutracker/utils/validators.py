from typing import Union, Optional

from ..enums import Url
from ..exceptions import RuTrackerDownloadError, RuTrackerAuthError


def validate_topic_id_or_url(topic_id_or_url: Union[int, str]) -> tuple[str, Optional[dict]]:
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
    elif isinstance(topic_id_or_url, str) and topic_id_or_url.startswith(Url.DOWNLOAD.value):
        url = topic_id_or_url
        params = None
        return url, params
    else:
        raise RuTrackerDownloadError(
            "Передан недопустимый параметр. Ожидался topic_id (int) "
            "или URL (str), начинающийся с 'https://rutracker.org/forum/dl.php?t='."
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
            f"Ошибка аутентификации: статус-код {status_code}"
        )
    if "cap_sid" in text:
        raise RuTrackerAuthError(
            "Найдена капча при аутентификации! Пройдите её в браузере и попробуйте еще раз!"
        )
    if not has_cookies:
        raise RuTrackerAuthError("Не удалось выполнить аутентификацию.")


def get_auth_data(login: str, password: str) -> dict:
    """
    Формирует данные для запроса аутентификации.

    :param login: Логин пользователя.
    :param password: Пароль пользователя.
    :return: Словарь с данными для POST-запроса.
    """
    return {
        'login_username': login,
        'login_password': password,
        'login': 'Вход'
    }


def build_search_params(title: str, page: int, page_size: int = 50) -> dict:
    """
    Формирует параметры для запроса поиска.

    :param title: Заголовок для поиска.
    :param page: Номер страницы (начинается с 1).
    :param page_size: Размер страницы (по умолчанию 50).
    :return: Словарь с параметрами запроса.
    """
    return {
        "start": (page - 1) * page_size,
        "nm": title,
    }

