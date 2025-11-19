import pytest

from py_rutracker.enums import Url
from py_rutracker.exceptions import (
    RuTrackerAuthError,
    RuTrackerDownloadError,
    RuTrackerValidationError,
)
from py_rutracker.utils.validators import (build_search_params, get_auth_data,
                                           validate_auth_response,
                                           validate_login_password,
                                           validate_search_page,
                                           validate_search_title,
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
        assert exc_info.value.topic_id_or_url == invalid_url
        assert "topic_id_or_url" in exc_info.value.context
    
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
        assert exc_info.value.status_code == 401
        assert "status_code=401" in str(exc_info.value)
    
    def test_validate_auth_with_captcha(self):
        """Тест валидации с обнаруженной капчей."""
        with pytest.raises(RuTrackerAuthError) as exc_info:
            validate_auth_response("cap_sid found", 200, True)
        assert "капча" in str(exc_info.value).lower()
        assert exc_info.value.status_code == 200
        assert "status_code=200" in str(exc_info.value)
    
    def test_validate_auth_without_cookies(self):
        """Тест валидации без cookies."""
        with pytest.raises(RuTrackerAuthError) as exc_info:
            validate_auth_response("success", 200, False)
        assert "аутентификацию" in str(exc_info.value).lower()
        assert exc_info.value.status_code == 200
        assert "status_code=200" in str(exc_info.value)


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
        """Тест с пустыми строками - должна быть ошибка валидации."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            get_auth_data("", "")
        assert "Логин не может быть пустым" in str(exc_info.value)
        assert exc_info.value.field_name == "login"


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
        """Тест с пустым заголовком - должна быть ошибка валидации."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            build_search_params("", 1)
        assert "Заголовок поиска не может быть пустым" in str(exc_info.value)
        assert exc_info.value.field_name == "title"
    
    def test_build_search_params_invalid_page(self):
        """Тест с невалидным номером страницы."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            build_search_params("test", 0)
        assert "Номер страницы должен быть больше 0" in str(exc_info.value)
        assert exc_info.value.field_name == "page"
        
        with pytest.raises(RuTrackerValidationError) as exc_info:
            build_search_params("test", -1)
        assert "Номер страницы должен быть больше 0" in str(exc_info.value)
        assert exc_info.value.field_name == "page"


class TestValidateLoginPassword:
    """Тесты для функции validate_login_password."""
    
    def test_validate_valid_login_password(self):
        """Тест валидации валидных логина и пароля."""
        validate_login_password("test_user", "test_password")
        validate_login_password("user123", "pass456")
        validate_login_password("a" * 3, "b" * 3)  # Минимальная длина
    
    def test_validate_empty_login(self):
        """Тест валидации с пустым логином."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_login_password("", "password")
        assert "Логин не может быть пустым" in str(exc_info.value)
        assert exc_info.value.field_name == "login"
        
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_login_password(None, "password")
        assert "Логин не может быть пустым" in str(exc_info.value)
        assert exc_info.value.field_name == "login"
    
    def test_validate_login_only_spaces(self):
        """Тест валидации логина, состоящего только из пробелов."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_login_password("   ", "password")
        assert "Логин не может быть пустым или состоять только из пробелов" in str(exc_info.value)
        assert exc_info.value.field_name == "login"
    
    def test_validate_login_too_short(self):
        """Тест валидации слишком короткого логина."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_login_password("ab", "password")
        assert "Логин должен содержать минимум 3 символа" in str(exc_info.value)
        assert exc_info.value.field_name == "login"
        
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_login_password("a", "password")
        assert "Логин должен содержать минимум 3 символа" in str(exc_info.value)
        assert exc_info.value.field_name == "login"
    
    def test_validate_empty_password(self):
        """Тест валидации с пустым паролем."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_login_password("login", "")
        assert "Пароль не может быть пустым" in str(exc_info.value)
        assert exc_info.value.field_name == "password"
        
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_login_password("login", None)
        assert "Пароль не может быть пустым" in str(exc_info.value)
        assert exc_info.value.field_name == "password"
    
    def test_validate_password_only_spaces(self):
        """Тест валидации пароля, состоящего только из пробелов."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_login_password("login", "   ")
        assert "Пароль не может быть пустым или состоять только из пробелов" in str(exc_info.value)
        assert exc_info.value.field_name == "password"
    
    def test_validate_password_too_short(self):
        """Тест валидации слишком короткого пароля."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_login_password("login", "ab")
        assert "Пароль должен содержать минимум 3 символа" in str(exc_info.value)
        assert exc_info.value.field_name == "password"
        
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_login_password("login", "a")
        assert "Пароль должен содержать минимум 3 символа" in str(exc_info.value)
        assert exc_info.value.field_name == "password"
    
    def test_validate_login_with_whitespace(self):
        """Тест валидации логина с пробелами в начале/конце."""
        validate_login_password("  test_user  ", "password")
    
    def test_validate_password_with_whitespace(self):
        """Тест валидации пароля с пробелами в начале/конце."""
        validate_login_password("login", "  password  ")


class TestValidateSearchTitle:
    """Тесты для функции validate_search_title."""
    
    def test_validate_valid_title(self):
        """Тест валидации валидного заголовка."""
        validate_search_title("test query")
        validate_search_title("Static-X")
        validate_search_title("a" * 200)  # Максимальная длина
    
    def test_validate_empty_title(self):
        """Тест валидации с пустым заголовком."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_search_title("")
        assert "Заголовок поиска не может быть пустым" in str(exc_info.value)
        assert exc_info.value.field_name == "title"
        
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_search_title(None)
        assert "Заголовок поиска не может быть пустым" in str(exc_info.value)
        assert exc_info.value.field_name == "title"
    
    def test_validate_title_only_spaces(self):
        """Тест валидации заголовка, состоящего только из пробелов."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_search_title("   ")
        assert "Заголовок поиска не может быть пустым или состоять только из пробелов" in str(exc_info.value)
        assert exc_info.value.field_name == "title"
    
    def test_validate_title_too_long(self):
        """Тест валидации слишком длинного заголовка."""
        long_title = "a" * 201
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_search_title(long_title)
        assert "Заголовок поиска не может быть длиннее 200 символов" in str(exc_info.value)
        assert exc_info.value.field_name == "title"
    
    def test_validate_title_with_whitespace(self):
        """Тест валидации заголовка с пробелами в начале/конце."""
        # Заголовок с пробелами должен быть валидным (они будут обрезаны)
        validate_search_title("  test query  ")


class TestValidateSearchPage:
    """Тесты для функции validate_search_page."""
    
    def test_validate_valid_page(self):
        """Тест валидации валидного номера страницы."""
        validate_search_page(1)
        validate_search_page(10)
        validate_search_page(100)
    
    def test_validate_page_zero(self):
        """Тест валидации нулевой страницы."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_search_page(0)
        assert "Номер страницы должен быть больше 0" in str(exc_info.value)
        assert exc_info.value.field_name == "page"
    
    def test_validate_page_negative(self):
        """Тест валидации отрицательного номера страницы."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_search_page(-1)
        assert "Номер страницы должен быть больше 0" in str(exc_info.value)
        assert exc_info.value.field_name == "page"
        
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_search_page(-10)
        assert "Номер страницы должен быть больше 0" in str(exc_info.value)
        assert exc_info.value.field_name == "page"
    
    def test_validate_page_not_int(self):
        """Тест валидации номера страницы не целого типа."""
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_search_page("1")
        assert "Номер страницы должен быть целым числом" in str(exc_info.value)
        assert exc_info.value.field_name == "page"
        
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_search_page(1.5)
        assert "Номер страницы должен быть целым числом" in str(exc_info.value)
        assert exc_info.value.field_name == "page"
        
        with pytest.raises(RuTrackerValidationError) as exc_info:
            validate_search_page(None)
        assert "Номер страницы должен быть целым числом" in str(exc_info.value)
        assert exc_info.value.field_name == "page"

