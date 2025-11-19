import requests

from py_rutracker.exceptions import (
    RuTrackerAuthError,
    RuTrackerRequestError,
    RuTrackerParsingError,
    RuTrackerValidationError,
    RuTrackerDownloadError,
)
from py_rutracker.utils.retry import (
    _is_retryable_exception,
    _is_not_retryable_exception,
    _is_retryable_status_code,
)


class TestIsRetryableStatusCode:
    """Тесты для функции _is_retryable_status_code."""
    
    def test_retryable_status_codes(self):
        """Тест временных ошибок сервера (5xx)."""
        assert _is_retryable_status_code(500) is True
        assert _is_retryable_status_code(502) is True
        assert _is_retryable_status_code(503) is True
        assert _is_retryable_status_code(504) is True
        assert _is_retryable_status_code(599) is True
    
    def test_non_retryable_status_codes(self):
        """Тест клиентских ошибок (4xx) и успешных ответов."""
        assert _is_retryable_status_code(400) is False
        assert _is_retryable_status_code(401) is False
        assert _is_retryable_status_code(403) is False
        assert _is_retryable_status_code(404) is False
        assert _is_retryable_status_code(200) is False
        assert _is_retryable_status_code(300) is False


class TestIsRetryableException:
    """Тесты для функции _is_retryable_exception."""
    
    def test_network_errors_retryable(self):
        """Тест сетевых ошибок requests."""
        assert _is_retryable_exception(requests.exceptions.ConnectionError("Connection failed")) is True
        assert _is_retryable_exception(requests.exceptions.Timeout("Timeout")) is True
        assert _is_retryable_exception(requests.exceptions.RequestException("Request failed")) is True
    
    def test_retryable_request_error_with_5xx(self):
        """Тест RuTrackerRequestError с временным статус-кодом."""
        error = RuTrackerRequestError(
            "Server error",
            url="https://example.com",
            status_code=500
        )
        assert _is_retryable_exception(error) is True
    
    def test_non_retryable_request_error_with_4xx(self):
        """Тест RuTrackerRequestError с клиентским статус-кодом."""
        error = RuTrackerRequestError(
            "Client error",
            url="https://example.com",
            status_code=404
        )
        assert _is_retryable_exception(error) is False
    
    def test_retryable_request_error_without_status(self):
        """Тест RuTrackerRequestError без статус-кода (сетевая ошибка)."""
        error = RuTrackerRequestError(
            "Ошибка при выполнении запроса: Connection failed",
            url="https://example.com"
        )
        assert _is_retryable_exception(error) is True
    
    def test_non_retryable_exceptions(self):
        """Тест исключений, которые не должны повторяться."""
        assert _is_retryable_exception(RuTrackerAuthError("Auth failed")) is False
        assert _is_retryable_exception(RuTrackerParsingError("Parsing failed")) is False
        assert _is_retryable_exception(RuTrackerValidationError("Validation failed")) is False
        assert _is_retryable_exception(RuTrackerDownloadError("Download failed")) is False


class TestIsNotRetryableException:
    """Тесты для функции _is_not_retryable_exception."""
    
    def test_auth_errors_not_retryable(self):
        """Тест ошибок аутентификации."""
        assert _is_not_retryable_exception(RuTrackerAuthError("Auth failed")) is True
        assert _is_not_retryable_exception(RuTrackerParsingError("Parsing failed")) is True
        assert _is_not_retryable_exception(RuTrackerValidationError("Validation failed")) is True
        assert _is_not_retryable_exception(RuTrackerDownloadError("Download failed")) is True
    
    def test_client_errors_not_retryable(self):
        """Тест клиентских ошибок (4xx)."""
        error = RuTrackerRequestError(
            "Client error",
            url="https://example.com",
            status_code=404
        )
        assert _is_not_retryable_exception(error) is True
    
    def test_auth_required_not_retryable(self):
        """Тест ошибок аутентификации в RuTrackerRequestError."""
        error = RuTrackerRequestError(
            "Необходима аутентификация.",
            url="https://example.com",
            status_code=200
        )
        assert _is_not_retryable_exception(error) is True
    
    def test_server_errors_retryable(self):
        """Тест временных ошибок сервера (5xx) - они должны повторяться."""
        error = RuTrackerRequestError(
            "Server error",
            url="https://example.com",
            status_code=500
        )
        assert _is_not_retryable_exception(error) is False
    
    def test_network_errors_retryable(self):
        """Тест сетевых ошибок - они должны повторяться."""
        assert _is_not_retryable_exception(requests.exceptions.ConnectionError("Connection failed")) is False

