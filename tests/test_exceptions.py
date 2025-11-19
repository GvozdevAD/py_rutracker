from py_rutracker.exceptions import (RuTrackerAuthError,
                                     RuTrackerDownloadError,
                                     RuTrackerException, RuTrackerParsingError,
                                     RuTrackerRequestError,
                                     RuTrackerValidationError)


class TestRuTrackerException:
    """Тесты для базового исключения RuTrackerException."""
    
    def test_exception_creation(self):
        """Тест создания базового исключения."""
        exc = RuTrackerException("Test error")
        assert str(exc) == "Test error"
        assert isinstance(exc, Exception)
        assert exc.message == "Test error"
        assert exc.context == {}
    
    def test_exception_with_context(self):
        """Тест создания исключения с контекстом."""
        exc = RuTrackerException("Test error", key1="value1", key2=123)
        assert exc.message == "Test error"
        assert exc.context == {"key1": "value1", "key2": 123}
        assert "key1=value1" in str(exc)
        assert "key2=123" in str(exc)


class TestRuTrackerAuthError:
    """Тесты для исключения RuTrackerAuthError."""
    
    def test_auth_error_creation(self):
        """Тест создания исключения аутентификации."""
        exc = RuTrackerAuthError("Auth failed")
        assert str(exc) == "Auth failed"
        assert isinstance(exc, RuTrackerException)
        assert isinstance(exc, Exception)
        assert exc.url is None
        assert exc.status_code is None
    
    def test_auth_error_with_context(self):
        """Тест создания исключения аутентификации с контекстом."""
        exc = RuTrackerAuthError(
            "Auth failed",
            url="https://example.com/auth",
            status_code=401
        )
        assert exc.url == "https://example.com/auth"
        assert exc.status_code == 401
        assert "url=https://example.com/auth" in str(exc)
        assert "status_code=401" in str(exc)
    
    def test_auth_error_with_additional_context(self):
        """Тест создания исключения с дополнительным контекстом."""
        exc = RuTrackerAuthError(
            "Auth failed",
            url="https://example.com/auth",
            status_code=401,
            login="test_user"
        )
        assert exc.url == "https://example.com/auth"
        assert exc.status_code == 401
        assert "login" in exc.context
        assert exc.context["login"] == "test_user"


class TestRuTrackerRequestError:
    """Тесты для исключения RuTrackerRequestError."""
    
    def test_request_error_creation(self):
        """Тест создания исключения запроса."""
        exc = RuTrackerRequestError("Request failed")
        assert str(exc) == "Request failed"
        assert isinstance(exc, RuTrackerException)
        assert isinstance(exc, Exception)
        assert exc.url is None
        assert exc.status_code is None
        assert exc.params is None
    
    def test_request_error_with_context(self):
        """Тест создания исключения запроса с контекстом."""
        params = {"page": 1, "query": "test"}
        exc = RuTrackerRequestError(
            "Request failed",
            url="https://example.com/search",
            status_code=500,
            params=params
        )
        assert exc.url == "https://example.com/search"
        assert exc.status_code == 500
        assert exc.params == params
        assert "url=https://example.com/search" in str(exc)
        assert "status_code=500" in str(exc)
        assert "params" in exc.context


class TestRuTrackerParsingError:
    """Тесты для исключения RuTrackerParsingError."""
    
    def test_parsing_error_creation(self):
        """Тест создания исключения парсинга."""
        exc = RuTrackerParsingError("Parsing failed")
        assert str(exc) == "Parsing failed"
        assert isinstance(exc, RuTrackerException)
        assert isinstance(exc, Exception)
        assert exc.html_snippet is None
        assert exc.selector is None
    
    def test_parsing_error_with_context(self):
        """Тест создания исключения парсинга с контекстом."""
        html = "<div>test</div>" * 50  # Длинный HTML
        exc = RuTrackerParsingError(
            "Parsing failed",
            html_snippet=html,
            selector="#tor-tbl"
        )
        assert exc.html_snippet == html
        assert exc.selector == "#tor-tbl"
        # Проверяем, что длинный HTML обрезается в контексте
        assert len(exc.context["html_snippet"]) <= 203  # 200 + "..."
        assert "selector=#tor-tbl" in str(exc)
    
    def test_parsing_error_html_truncation(self):
        """Тест обрезки длинного HTML фрагмента."""
        long_html = "a" * 300
        exc = RuTrackerParsingError("Parsing failed", html_snippet=long_html)
        assert exc.html_snippet == long_html  # Оригинал сохраняется
        assert len(exc.context["html_snippet"]) == 203  # Обрезается в контексте
        assert exc.context["html_snippet"].endswith("...")


class TestRuTrackerDownloadError:
    """Тесты для исключения RuTrackerDownloadError."""
    
    def test_download_error_creation(self):
        """Тест создания исключения скачивания."""
        exc = RuTrackerDownloadError("Download failed")
        assert str(exc) == "Download failed"
        assert isinstance(exc, RuTrackerException)
        assert isinstance(exc, Exception)
        assert exc.topic_id_or_url is None
        assert exc.url is None
        assert exc.status_code is None
    
    def test_download_error_with_context(self):
        """Тест создания исключения скачивания с контекстом."""
        exc = RuTrackerDownloadError(
            "Download failed",
            topic_id_or_url=12345,
            url="https://example.com/download",
            status_code=404
        )
        assert exc.topic_id_or_url == 12345
        assert exc.url == "https://example.com/download"
        assert exc.status_code == 404
        assert "topic_id_or_url=12345" in str(exc)
        assert "url=https://example.com/download" in str(exc)
        assert "status_code=404" in str(exc)
    
    def test_download_error_with_url_string(self):
        """Тест создания исключения с URL строкой."""
        url_string = "https://rutracker.org/forum/dl.php?t=12345"
        exc = RuTrackerDownloadError(
            "Download failed",
            topic_id_or_url=url_string
        )
        assert exc.topic_id_or_url == url_string
        assert "topic_id_or_url" in exc.context


class TestRuTrackerValidationError:
    """Тесты для исключения RuTrackerValidationError."""
    
    def test_validation_error_creation(self):
        """Тест создания исключения валидации."""
        exc = RuTrackerValidationError("Validation failed")
        assert str(exc) == "Validation failed"
        assert isinstance(exc, RuTrackerException)
        assert isinstance(exc, Exception)
        assert exc.field_name is None
        assert exc.field_value is None
    
    def test_validation_error_with_context(self):
        """Тест создания исключения валидации с контекстом."""
        exc = RuTrackerValidationError(
            "Validation failed",
            field_name="login",
            field_value="ab"
        )
        assert exc.field_name == "login"
        assert exc.field_value == "ab"
        assert "field_name=login" in str(exc)
        assert "field_value=ab" in str(exc)
    
    def test_validation_error_with_additional_context(self):
        """Тест создания исключения с дополнительным контекстом."""
        exc = RuTrackerValidationError(
            "Validation failed",
            field_name="title",
            field_value="a" * 201,
            min_length=3,
            max_length=200
        )
        assert exc.field_name == "title"
        assert exc.field_value == "a" * 201
        assert "min_length" in exc.context
        assert exc.context["min_length"] == 3
        assert "max_length" in exc.context
        assert exc.context["max_length"] == 200

