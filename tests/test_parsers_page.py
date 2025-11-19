from py_rutracker.models.search import SearchResult
from py_rutracker.parsers.page import ParsingPage


class TestParsingPage:
    """Тесты для класса ParsingPage."""
    
    def test_search_with_valid_html(self, mock_html_search_results):
        """Тест парсинга валидного HTML."""
        parser = ParsingPage()
        results = parser.search(mock_html_search_results)
        
        assert len(results) == 1
        assert isinstance(results[0], SearchResult)
        assert results[0].topic_id == 12345
        assert results[0].title == "Test Movie"
        assert results[0].category == "Фильмы"
    
    def test_search_with_dict_format(self, mock_html_search_results):
        """Тест парсинга с возвратом словарей."""
        parser = ParsingPage()
        results = parser.search(mock_html_search_results, return_dict_format=True)
        
        assert len(results) == 1
        assert isinstance(results[0], dict)
        assert results[0]["topic_id"] == 12345
        assert results[0]["title"] == "Test Movie"
    
    def test_search_with_empty_html(self):
        """Тест парсинга пустого HTML."""
        parser = ParsingPage()
        results = parser.search("<html><body></body></html>")
        assert len(results) == 0
    
    def test_search_without_table(self):
        """Тест парсинга HTML без таблицы результатов."""
        html = "<html><body><div>No table here</div></body></html>"
        parser = ParsingPage()
        results = parser.search(html)
        assert len(results) == 0
    
    def test_search_with_closed_topic(self):
        """Тест что закрытые топики пропускаются."""
        html = """
        <html>
        <body>
            <table id="tor-tbl">
                <tbody>
                    <tr>
                        <td></td>
                        <td title="закрыто"></td>
                        <td><a href="viewforum.php?f=123">Фильмы</a></td>
                        <td><a href="viewtopic.php?t=12345" data-topic_id="12345">Test Movie</a></td>
                        <td><a href="profile.php?u=1">Author</a></td>
                        <td data-ts_text="1073741824"><a href="dl.php?t=12345">Download</a></td>
                        <td>10</td>
                        <td>5</td>
                        <td>100</td>
                        <td data-ts_text="1609459200">01-01-2021 00:00:00</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        parser = ParsingPage()
        results = parser.search(html)
        assert len(results) == 0
    
    def test_search_multiple_results(self):
        """Тест парсинга нескольких результатов."""
        html = """
        <html>
        <body>
            <table id="tor-tbl">
                <tbody>
                    <tr>
                        <td></td>
                        <td title="проверено"></td>
                        <td><a href="viewforum.php?f=123">Фильмы</a></td>
                        <td><a href="viewtopic.php?t=1" data-topic_id="1">Movie 1</a></td>
                        <td><a href="profile.php?u=1">Author1</a></td>
                        <td data-ts_text="1073741824"><a href="dl.php?t=1">Download</a></td>
                        <td>10</td>
                        <td>5</td>
                        <td>100</td>
                        <td data-ts_text="1609459200">01-01-2021 00:00:00</td>
                    </tr>
                    <tr>
                        <td></td>
                        <td title="проверено"></td>
                        <td><a href="viewforum.php?f=123">Фильмы</a></td>
                        <td><a href="viewtopic.php?t=2" data-topic_id="2">Movie 2</a></td>
                        <td><a href="profile.php?u=2">Author2</a></td>
                        <td data-ts_text="2147483648"><a href="dl.php?t=2">Download</a></td>
                        <td>20</td>
                        <td>10</td>
                        <td>200</td>
                        <td data-ts_text="1609545600">02-01-2021 00:00:00</td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        parser = ParsingPage()
        results = parser.search(html)
        assert len(results) == 2
        assert results[0].topic_id == 1
        assert results[1].topic_id == 2
    
    def test_search_size_formatting(self, mock_html_search_results):
        """Тест форматирования размера."""
        parser = ParsingPage()
        results = parser.search(mock_html_search_results)
        assert results[0].size == 1.0
        assert results[0].unit == "GB"
    
    def test_search_with_missing_info_row(self):
        """Тест обработки отсутствующих данных в строке."""
        html = """
        <html>
        <body>
            <table id="tor-tbl">
                <tbody>
                    <tr>
                        <td></td>
                    </tr>
                </tbody>
            </table>
        </body>
        </html>
        """
        parser = ParsingPage()
        results = parser.search(html)
        assert len(results) == 0

