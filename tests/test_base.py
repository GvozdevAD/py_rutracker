from unittest.mock import patch

import pytest

from py_rutracker.core.base import BaseRuTrackerClient
from py_rutracker.enums import Url
from py_rutracker.exceptions import (RuTrackerDownloadError,
                                     RuTrackerParsingError)
from py_rutracker.models.search import SearchResult
from py_rutracker.models.search_form import SearchFormData


class ConcreteClient(BaseRuTrackerClient):
    """Конкретная реализация для тестирования абстрактного класса."""
    
    def search(self, title: str, page: int = 1, return_search_dict: bool = False):
        return []
    
    def get_torrent(self, topic_id_or_url):
        return b"torrent data"
    
    def download(self, topic_id_or_url, save_path=None, filename=None):
        return "path/to/file.torrent"
    
    def get_search_form(self, force_refresh: bool = False):
        return SearchFormData()


class TestBaseRuTrackerClient:
    """Тесты для базового класса BaseRuTrackerClient."""
    
    def test_init(self):
        """Тест инициализации."""
        client = ConcreteClient("login", "password")
        assert client._login == "login"
        assert client._password == "password"
        assert client.parser is not None
        assert client._search_form_cache is None
    
    def test_get_auth_data(self):
        """Тест получения данных аутентификации."""
        client = ConcreteClient("test_login", "test_password")
        auth_data = client._get_auth_data()
        assert auth_data["login_username"] == "test_login"
        assert auth_data["login_password"] == "test_password"
        assert auth_data["login"] == "Вход"
    
    def test_validate_auth_response_success(self):
        """Тест успешной валидации ответа аутентификации."""
        client = ConcreteClient("login", "password")
        # Не должно быть исключения
        client._validate_auth_response("success", 200, True)
    
    def test_validate_auth_response_failure(self):
        """Тест неуспешной валидации ответа аутентификации."""
        client = ConcreteClient("login", "password")
        from py_rutracker.exceptions import RuTrackerAuthError
        with pytest.raises(RuTrackerAuthError):
            client._validate_auth_response("error", 401, False)
    
    def test_build_search_params(self):
        """Тест построения параметров поиска."""
        client = ConcreteClient("login", "password")
        params = client._build_search_params("test query", 2)
        assert params["nm"] == "test query"
        assert params["start"] == 50  # (2-1) * 50
    
    def test_parse_search_results(self, mock_html_search_results):
        """Тест парсинга результатов поиска."""
        client = ConcreteClient("login", "password")
        results = client._parse_search_results(mock_html_search_results)
        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
    
    def test_parse_search_results_dict_format(self, mock_html_search_results):
        """Тест парсинга результатов в формате словаря."""
        client = ConcreteClient("login", "password")
        results = client._parse_search_results(mock_html_search_results, return_search_dict=True)
        assert len(results) == 1
        assert isinstance(results[0], dict)
    
    def test_parse_search_results_error(self):
        """Тест обработки ошибки парсинга."""
        client = ConcreteClient("login", "password")
        with patch.object(client.parser, 'search', side_effect=Exception("Parse error")):
            with pytest.raises(RuTrackerParsingError):
                client._parse_search_results("invalid html")
    
    def test_validate_download_params_with_topic_id(self):
        """Тест валидации параметров скачивания с topic_id."""
        client = ConcreteClient("login", "password")
        url, params = client._validate_download_params(12345)
        assert url == Url.DOWNLOAD.value
        assert params == {"t": 12345}
    
    def test_validate_download_params_with_url(self):
        """Тест валидации параметров скачивания с URL."""
        client = ConcreteClient("login", "password")
        download_url = f"{Url.DOWNLOAD.value}?t=12345"
        url, params = client._validate_download_params(download_url)
        assert url == download_url
        assert params is None
    
    def test_validate_download_params_invalid(self):
        """Тест валидации невалидных параметров."""
        client = ConcreteClient("login", "password")
        with pytest.raises(RuTrackerDownloadError):
            client._validate_download_params("invalid")
    
    def test_get_search_url(self):
        """Тест получения URL поиска."""
        client = ConcreteClient("login", "password")
        assert client._get_search_url() == Url.SEARCH.value
    
    def test_get_download_url(self):
        """Тест получения URL скачивания."""
        client = ConcreteClient("login", "password")
        assert client._get_download_url() == Url.DOWNLOAD.value
    
    def test_get_max_pages(self):
        """Тест получения максимального количества страниц."""
        client = ConcreteClient("login", "password")
        assert client._get_max_pages() > 0
    
    def test_extract_topic_id_from_url_with_int(self):
        """Тест извлечения topic_id из int."""
        client = ConcreteClient("login", "password")
        assert client._extract_topic_id_from_url(12345) == 12345
    
    def test_extract_topic_id_from_url_with_url(self):
        """Тест извлечения topic_id из URL."""
        client = ConcreteClient("login", "password")
        url = f"{Url.DOWNLOAD.value}?t=12345"
        assert client._extract_topic_id_from_url(url) == 12345
    
    def test_extract_topic_id_from_url_invalid(self):
        """Тест извлечения topic_id из невалидного URL."""
        client = ConcreteClient("login", "password")
        assert client._extract_topic_id_from_url("invalid") is None
    
    def test_prepare_download_path_default(self, temp_dir):
        """Тест подготовки пути скачивания по умолчанию."""
        client = ConcreteClient("login", "password")
        with patch('py_rutracker.core.base.Path.cwd', return_value=temp_dir):
            path = client._prepare_download_path(12345)
            assert path.name == "12345.torrent"
            assert path.parent == temp_dir
    
    def test_prepare_download_path_custom(self, temp_dir):
        """Тест подготовки пути скачивания с кастомными параметрами."""
        client = ConcreteClient("login", "password")
        save_path = temp_dir / "downloads"
        path = client._prepare_download_path(12345, save_path=str(save_path), filename="custom")
        assert path.name == "custom.torrent"
        assert path.parent == save_path
    
    def test_prepare_download_path_without_extension(self, temp_dir):
        """Тест добавления расширения .torrent."""
        client = ConcreteClient("login", "password")
        path = client._prepare_download_path(12345, filename="test")
        assert path.name == "test.torrent"
    
    def test_is_search_form_cache_valid_no_cache(self):
        """Тест проверки валидности кеша когда кеша нет."""
        client = ConcreteClient("login", "password")
        assert client._is_search_form_cache_valid() is False
    
    def test_is_search_form_cache_valid_with_cache(self):
        """Тест проверки валидности кеша когда кеш есть."""
        client = ConcreteClient("login", "password")
        form_data = SearchFormData()
        client._set_search_form_cache(form_data)
        assert client._is_search_form_cache_valid() is True
    
    def test_get_search_form_cache(self):
        """Тест получения данных из кеша."""
        client = ConcreteClient("login", "password")
        form_data = SearchFormData()
        client._set_search_form_cache(form_data)
        cached = client._get_search_form_cache()
        assert cached == form_data
    
    def test_get_search_form_cache_invalid(self):
        """Тест получения данных из невалидного кеша."""
        client = ConcreteClient("login", "password")
        assert client._get_search_form_cache() is None
    
    def test_set_search_form_cache(self):
        """Тест установки кеша."""
        client = ConcreteClient("login", "password")
        form_data = SearchFormData()
        client._set_search_form_cache(form_data)
        assert client._search_form_cache is not None
        assert client._search_form_cache["data"] == form_data
    
    def test_clear_search_form_cache(self):
        """Тест очистки кеша."""
        client = ConcreteClient("login", "password")
        form_data = SearchFormData()
        client._set_search_form_cache(form_data)
        client._clear_search_form_cache()
        assert client._search_form_cache is None

