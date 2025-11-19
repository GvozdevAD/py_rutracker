from py_rutracker.core.constants import (DEFAULT_MAX_SEARCH_PAGES,
                                         DEFAULT_USER_AGENT, SEARCH_PAGE_SIZE)


class TestConstants:
    """Тесты для констант."""
    
    def test_search_page_size(self):
        """Тест размера страницы поиска."""
        assert SEARCH_PAGE_SIZE == 50
        assert isinstance(SEARCH_PAGE_SIZE, int)
        assert SEARCH_PAGE_SIZE > 0
    
    def test_default_max_search_pages(self):
        """Тест максимального количества страниц поиска."""
        assert DEFAULT_MAX_SEARCH_PAGES == 10
        assert isinstance(DEFAULT_MAX_SEARCH_PAGES, int)
        assert DEFAULT_MAX_SEARCH_PAGES > 0
    
    def test_default_user_agent(self):
        """Тест User-Agent по умолчанию."""
        assert isinstance(DEFAULT_USER_AGENT, str)
        assert len(DEFAULT_USER_AGENT) > 0
        assert "Mozilla" in DEFAULT_USER_AGENT

