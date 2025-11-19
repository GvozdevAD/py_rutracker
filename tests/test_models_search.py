import pytest
from pydantic import ValidationError

from py_rutracker.models.search import SearchResult


class TestSearchResult:
    """Тесты для модели SearchResult."""
    
    def test_create_valid_search_result(self, sample_search_result_dict):
        """Тест создания валидного результата поиска."""
        result = SearchResult(**sample_search_result_dict)
        assert result.topic_id == 12345
        assert result.title == "Test Movie"
        assert result.author == "Author"
        assert result.size == 1.0
        assert result.unit == "GB"
    
    def test_search_result_with_minimal_data(self):
        """Тест создания результата с минимальными данными."""
        data = {
            "topic_id": 1,
            "approved": "",
            "category": "Test",
            "title": "Test Title",
            "author": "Test Author",
            "size": 0.0,
            "unit": "KB",
            "download_url": "https://example.com/dl.php?t=1",
            "added": "01-01-2021 00:00:00"
        }
        result = SearchResult(**data)
        assert result.topic_id == 1
        assert result.seedmed == 0
        assert result.leechmed == 0
        assert result.download_counter == 0
    
    def test_search_result_with_optional_urls(self):
        """Тест с опциональными URL."""
        data = {
            "topic_id": 1,
            "approved": "",
            "category": "Test",
            "title": "Test",
            "title_url": None,
            "author": "Author",
            "author_url": "",
            "size": 1.0,
            "unit": "MB",
            "download_url": "https://example.com/dl.php?t=1",
            "added": "01-01-2021 00:00:00"
        }
        result = SearchResult(**data)
        assert result.title_url is None
        assert result.author_url is None
    
    def test_search_result_topic_id_validation(self):
        """Тест валидации topic_id."""
        data = {
            "topic_id": 0,
            "approved": "",
            "category": "Test",
            "title": "Test",
            "author": "Author",
            "size": 1.0,
            "unit": "MB",
            "download_url": "https://example.com/dl.php?t=1",
            "added": "01-01-2021 00:00:00"
        }
        with pytest.raises(ValidationError):
            SearchResult(**data)
    
    def test_search_result_size_validation(self):
        """Тест валидации размера."""
        data = {
            "topic_id": 1,
            "approved": "",
            "category": "Test",
            "title": "Test",
            "author": "Author",
            "size": -1.0,
            "unit": "MB",
            "download_url": "https://example.com/dl.php?t=1",
            "added": "01-01-2021 00:00:00"
        }
        with pytest.raises(ValidationError):
            SearchResult(**data)
    
    def test_search_result_string_conversion(self):
        """Тест преобразования в строку."""
        data = {
            "topic_id": 12345,
            "approved": "проверено",
            "category": "Фильмы",
            "title": "Test Movie",
            "author": "Author",
            "size": 1.0,
            "unit": "GB",
            "download_url": "https://example.com/dl.php?t=12345",
            "added": "01-01-2021 00:00:00"
        }
        result = SearchResult(**data)
        str_repr = str(result)
        assert "Topic ID: 12345" in str_repr
        assert "Title: Test Movie" in str_repr
        assert "Author: Author" in str_repr
    
    def test_search_result_model_dump_dict(self, sample_search_result_dict):
        """Тест метода model_dump_dict."""
        result = SearchResult(**sample_search_result_dict)
        dumped = result.model_dump_dict()
        assert isinstance(dumped, dict)
        assert dumped["topic_id"] == 12345
        assert dumped["title"] == "Test Movie"
    
    def test_search_result_seedmed_leechmed_validation(self):
        """Тест валидации seedmed и leechmed."""
        data = {
            "topic_id": 1,
            "approved": "",
            "category": "Test",
            "title": "Test",
            "author": "Author",
            "size": 1.0,
            "unit": "MB",
            "download_url": "https://example.com/dl.php?t=1",
            "seedmed": "10",
            "leechmed": "5",
            "download_counter": "100",
            "added": "01-01-2021 00:00:00"
        }
        result = SearchResult(**data)
        assert result.seedmed == 10
        assert result.leechmed == 5
        assert result.download_counter == 100
    
    def test_search_result_negative_values_converted_to_zero(self):
        """Тест что отрицательные значения преобразуются в 0."""
        data = {
            "topic_id": 1,
            "approved": "",
            "category": "Test",
            "title": "Test",
            "author": "Author",
            "size": 1.0,
            "unit": "MB",
            "download_url": "https://example.com/dl.php?t=1",
            "seedmed": -5,
            "leechmed": -3,
            "download_counter": -1,
            "added": "01-01-2021 00:00:00"
        }
        result = SearchResult(**data)
        assert result.seedmed == 0
        assert result.leechmed == 0
        assert result.download_counter == 0
    
    def test_search_result_none_values_converted_to_zero(self):
        """Тест что None значения преобразуются в 0."""
        data = {
            "topic_id": 1,
            "approved": "",
            "category": "Test",
            "title": "Test",
            "author": "Author",
            "size": 1.0,
            "unit": "MB",
            "download_url": "https://example.com/dl.php?t=1",
            "seedmed": None,
            "leechmed": None,
            "download_counter": None,
            "added": "01-01-2021 00:00:00"
        }
        result = SearchResult(**data)
        assert result.seedmed == 0
        assert result.leechmed == 0
        assert result.download_counter == 0

