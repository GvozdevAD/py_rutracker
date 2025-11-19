import aiohttp
import requests

from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type,
    retry_if_exception,
)

from ..exceptions import RuTrackerRequestError


def _is_retryable_status_code(status_code: int) -> bool:
    """
    Проверяет, является ли статус-код временной ошибкой, для которой стоит повторить запрос.
    
    :param status_code: HTTP статус-код.
    :return: True, если статус-код указывает на временную ошибку (5xx).
    """
    return 500 <= status_code < 600


def _is_retryable_exception(exception: Exception) -> bool:
    """
    Проверяет, является ли исключение сетевой ошибкой, для которой стоит повторить запрос.
    
    :param exception: Исключение для проверки.
    :return: True, если исключение указывает на сетевую ошибку.
    """
    if isinstance(exception, (
        requests.exceptions.ConnectionError,
        requests.exceptions.Timeout,
        requests.exceptions.RequestException,
    )):
        return True
    
    if isinstance(exception, RuTrackerRequestError):
        if exception.status_code is not None:
            return _is_retryable_status_code(exception.status_code)
        return "Ошибка при выполнении запроса" in str(exception)
    
    return False


def _is_not_retryable_exception(exception: Exception) -> bool:
    """
    Проверяет, является ли исключение ошибкой, для которой НЕ стоит повторять запрос.
    
    :param exception: Исключение для проверки.
    :return: True, если исключение указывает на ошибку, которую не нужно повторять.
    """
    from ..exceptions import (
        RuTrackerAuthError,
        RuTrackerParsingError,
        RuTrackerValidationError,
        RuTrackerDownloadError,
    )
    
    if isinstance(exception, (
        RuTrackerAuthError,
        RuTrackerParsingError,
        RuTrackerValidationError,
        RuTrackerDownloadError,
    )):
        return True
    
    if isinstance(exception, RuTrackerRequestError):
        if exception.status_code is not None:
            if 400 <= exception.status_code < 500:
                return True
            if "Необходима аутентификация" in str(exception):
                return True
    
    return False


def retry_on_network_error(
    max_attempts: int = 3,
    min_wait: float = 2.0,
    max_wait: float = 10.0,
    multiplier: float = 1.0,
):
    """
    Декоратор для повторных попыток при сетевых ошибках (синхронные функции).
    
    :param max_attempts: Максимальное количество попыток (по умолчанию 3).
    :param min_wait: Минимальное время ожидания между попытками в секундах (по умолчанию 2.0).
    :param max_wait: Максимальное время ожидания между попытками в секундах (по умолчанию 10.0).
    :param multiplier: Множитель для экспоненциальной задержки (по умолчанию 1.0).
    :return: Декоратор для применения к функции.
    """
    def retry_if_network_error(exception: Exception) -> bool:
        """Проверяет, нужно ли повторять запрос при данном исключении."""
        if _is_not_retryable_exception(exception):
            return False
        return _is_retryable_exception(exception)
    
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=multiplier, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
        )) | retry_if_exception(retry_if_network_error),
        reraise=True,
    )


def async_retry_on_network_error(
    max_attempts: int = 3,
    min_wait: float = 2.0,
    max_wait: float = 10.0,
    multiplier: float = 1.0,
):
    """
    Декоратор для повторных попыток при сетевых ошибках (асинхронные функции).
    
    :param max_attempts: Максимальное количество попыток (по умолчанию 3).
    :param min_wait: Минимальное время ожидания между попытками в секундах (по умолчанию 2.0).
    :param max_wait: Максимальное время ожидания между попытками в секундах (по умолчанию 10.0).
    :param multiplier: Множитель для экспоненциальной задержки (по умолчанию 1.0).
    :return: Декоратор для применения к асинхронной функции.
    """
    def retry_if_network_error(exception: Exception) -> bool:
        """Проверяет, нужно ли повторять запрос при данном исключении."""
        if _is_not_retryable_exception(exception):
            return False
        return _is_retryable_exception(exception)
    
    return retry(
        stop=stop_after_attempt(max_attempts),
        wait=wait_exponential(multiplier=multiplier, min=min_wait, max=max_wait),
        retry=retry_if_exception_type((
            aiohttp.ClientError,
            aiohttp.ClientConnectionError,
            aiohttp.ClientTimeout,
            aiohttp.ServerTimeoutError,
        )) | retry_if_exception(retry_if_network_error),
        reraise=True,
    )

