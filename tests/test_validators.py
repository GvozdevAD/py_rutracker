import pytest

from py_rutracker.enums import Url
from py_rutracker.exceptions import RuTrackerAuthError, RuTrackerDownloadError
from py_rutracker.utils.validators import (build_search_params, get_auth_data,
                                           validate_auth_response,
                                           validate_topic_id_or_url)


class TestValidateTopicIdOrUrl:
    """Тесты для функции validate_topic_id_or_url."""
    
    def test_validate_with_topic_id(self):
        """Тест валидации с topic_id (int)."""
        url, params = validate_topic_id_or_url(12345)
        assert url == Url.DOWNLOAD.value
        assert params == {"t": 12345}
    
    def test_validate_with_valid_url(self):
        """Тест валидации с валидным URL."""
        valid_url = f"{Url.DOWNLOAD.value}?t=12345"
        url, params = validate_topic_id_or_url(valid_url)
        assert url == valid_url
        assert params is None
    
    def test_validate_with_invalid_url(self):
        """Тест валидации с невалидным URL."""
        invalid_url = "https://example.com/torrent"
        with pytest.raises(RuTrackerDownloadError) as exc_info:
            validate_topic_id_or_url(invalid_url)
        assert "недопустимый параметр" in str(exc_info.value).lower()
    
    def test_validate_with_invalid_type(self):
        """Тест валидации с невалидным типом."""
        with pytest.raises(RuTrackerDownloadError):
            validate_topic_id_or_url(None)
        with pytest.raises(RuTrackerDownloadError):
            validate_topic_id_or_url([])


class TestValidateAuthResponse:
    """Тесты для функции validate_auth_response."""
    
    def test_validate_successful_auth(self):
        """Тест успешной аутентификации."""
        validate_auth_response("success", 200, True)
    
    def test_validate_auth_with_wrong_status_code(self):
        """Тест валидации с неправильным статус-кодом."""
        with pytest.raises(RuTrackerAuthError) as exc_info:
            validate_auth_response("error", 401, True)
        assert "статус-код 401" in str(exc_info.value)
    
    def test_validate_auth_with_captcha(self):
        """Тест валидации с обнаруженной капчей."""
        with pytest.raises(RuTrackerAuthError) as exc_info:
            validate_auth_response("cap_sid found", 200, True)
        assert "капча" in str(exc_info.value).lower()
    
    def test_validate_auth_without_cookies(self):
        """Тест валидации без cookies."""
        with pytest.raises(RuTrackerAuthError) as exc_info:
            validate_auth_response("success", 200, False)
        assert "аутентификацию" in str(exc_info.value).lower()


class TestGetAuthData:
    """Тесты для функции get_auth_data."""
    
    def test_get_auth_data(self):
        """Тест получения данных аутентификации."""
        login = "test_user"
        password = "test_password"
        data = get_auth_data(login, password)
        
        assert isinstance(data, dict)
        assert data["login_username"] == login
        assert data["login_password"] == password
        assert data["login"] == "Вход"
    
    def test_get_auth_data_empty_strings(self):
        """Тест с пустыми строками."""
        data = get_auth_data("", "")
        assert data["login_username"] == ""
        assert data["login_password"] == ""


class TestBuildSearchParams:
    """Тесты для функции build_search_params."""
    
    def test_build_search_params_default_page_size(self):
        """Тест построения параметров поиска с размером страницы по умолчанию."""
        params = build_search_params("test query", 1)
        assert params["nm"] == "test query"
        assert params["start"] == 0
    
    def test_build_search_params_custom_page_size(self):
        """Тест построения параметров поиска с кастомным размером страницы."""
        params = build_search_params("test query", 2, page_size=25)
        assert params["nm"] == "test query"
        assert params["start"] == 25
    
    def test_build_search_params_multiple_pages(self):
        """Тест построения параметров для разных страниц."""
        params_page_1 = build_search_params("query", 1)
        params_page_2 = build_search_params("query", 2)
        params_page_3 = build_search_params("query", 3)
        
        assert params_page_1["start"] == 0
        assert params_page_2["start"] == 50
        assert params_page_3["start"] == 100
    
    def test_build_search_params_empty_title(self):
        """Тест с пустым заголовком."""
        params = build_search_params("", 1)
        assert params["nm"] == ""
        assert params["start"] == 0

