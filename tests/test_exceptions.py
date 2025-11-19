from py_rutracker.exceptions import (RuTrackerAuthError,
                                     RuTrackerDownloadError,
                                     RuTrackerException, RuTrackerParsingError,
                                     RuTrackerRequestError)


class TestRuTrackerException:
    """Тесты для базового исключения RuTrackerException."""
    
    def test_exception_creation(self):
        """Тест создания базового исключения."""
        exc = RuTrackerException("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)


class TestRuTrackerAuthError:
    """Тесты для исключения RuTrackerAuthError."""
    
    def test_auth_error_creation(self):
        """Тест создания исключения аутентификации."""
        exc = RuTrackerAuthError("Auth failed")
        assert str(exc) == "Auth failed"
        assert isinstance(exc, RuTrackerException)
        assert isinstance(exc, Exception)


class TestRuTrackerRequestError:
    """Тесты для исключения RuTrackerRequestError."""
    
    def test_request_error_creation(self):
        """Тест создания исключения запроса."""
        exc = RuTrackerRequestError("Request failed")
        assert str(exc) == "Request failed"
        assert isinstance(exc, RuTrackerException)
        assert isinstance(exc, Exception)


class TestRuTrackerParsingError:
    """Тесты для исключения RuTrackerParsingError."""
    
    def test_parsing_error_creation(self):
        """Тест создания исключения парсинга."""
        exc = RuTrackerParsingError("Parsing failed")
        assert str(exc) == "Parsing failed"
        assert isinstance(exc, RuTrackerException)
        assert isinstance(exc, Exception)


class TestRuTrackerDownloadError:
    """Тесты для исключения RuTrackerDownloadError."""
    
    def test_download_error_creation(self):
        """Тест создания исключения скачивания."""
        exc = RuTrackerDownloadError("Download failed")
        assert str(exc) == "Download failed"
        assert isinstance(exc, RuTrackerException)
        assert isinstance(exc, Exception)

