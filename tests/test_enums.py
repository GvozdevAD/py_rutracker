from py_rutracker.enums import Url


class TestUrl:
    """Тесты для перечисления Url."""
    
    def test_url_values(self):
        """Тест проверки значений URL."""
        assert Url.HOST.value == "https://rutracker.org"
        assert Url.FORUM.value == "https://rutracker.org/forum"
        assert Url.INDEX.value == "https://rutracker.org/forum/index.php"
        assert Url.AUTH.value == "https://rutracker.org/forum/login.php"
        assert Url.SEARCH.value == "https://rutracker.org/forum/tracker.php"
        assert Url.VIEWTOPIC.value == "https://rutracker.org/forum/viewtopic.php"
        assert Url.DOWNLOAD.value == "https://rutracker.org/forum/dl.php"
    
    def test_url_enum_membership(self):
        """Тест принадлежности к перечислению."""
        assert isinstance(Url.HOST, Url)
        assert Url.HOST in Url
    
    def test_url_string_representation(self):
        """Тест строкового представления."""
        assert str(Url.HOST) == "Url.HOST"
        assert repr(Url.HOST) == "<Url.HOST: 'https://rutracker.org'>"

