from py_rutracker.models.search_form import SearchFormData
from py_rutracker.parsers.search_form import SearchFormParser


class TestSearchFormParser:
    """Тесты для класса SearchFormParser."""
    
    def test_parse_valid_html(self, mock_html_search_form):
        """Тест парсинга валидного HTML формы."""
        parser = SearchFormParser()
        form_data = parser.parse(mock_html_search_form)
        
        assert isinstance(form_data, SearchFormData)
        assert len(form_data.forum_groups) > 0
        assert len(form_data.sort_options) > 0
        assert len(form_data.sort_directions) > 0
        assert len(form_data.time_filter_options) > 0
    
    def test_parse_forum_groups(self, mock_html_search_form):
        """Тест парсинга групп разделов."""
        parser = SearchFormParser()
        form_data = parser.parse(mock_html_search_form)
        
        assert len(form_data.forum_groups) >= 2
        films_group = next((g for g in form_data.forum_groups if g.name == "Фильмы"), None)
        assert films_group is not None
        assert len(films_group.sections) > 0
    
    def test_parse_forum_sections_properties(self, mock_html_search_form):
        parser = SearchFormParser()
        form_data = parser.parse(mock_html_search_form)
        
        all_sections = []
        for group in form_data.forum_groups:
            all_sections.extend(group.sections)
        
        root_sections = [s for s in all_sections if s.is_root]
        assert len(root_sections) > 0
    
    def test_parse_sort_options(self, mock_html_search_form):
        """Тест парсинга опций сортировки."""
        parser = SearchFormParser()
        form_data = parser.parse(mock_html_search_form)
        
        assert len(form_data.sort_options) >= 2
        date_option = next((o for o in form_data.sort_options if "дате" in o.name), None)
        assert date_option is not None
        assert date_option.form_field_name == "o"
    
    def test_parse_sort_directions(self, mock_html_search_form):
        """Тест парсинга направлений сортировки."""
        parser = SearchFormParser()
        form_data = parser.parse(mock_html_search_form)
        
        assert len(form_data.sort_directions) >= 2
        asc_direction = next((d for d in form_data.sort_directions if d.value == 1), None)
        assert asc_direction is not None
        assert asc_direction.form_field_name == "s"
    
    def test_parse_time_filters(self, mock_html_search_form):
        """Тест парсинга фильтров по времени."""
        parser = SearchFormParser()
        form_data = parser.parse(mock_html_search_form)
        
        assert len(form_data.time_filter_options) >= 2
        all_time_option = next((t for t in form_data.time_filter_options if t.value == 0), None)
        assert all_time_option is not None
        assert all_time_option.form_field_name == "tm"
    
    def test_parse_empty_html(self):
        """Тест парсинга пустого HTML."""
        parser = SearchFormParser()
        form_data = parser.parse("<html><body></body></html>")
        
        assert isinstance(form_data, SearchFormData)
        assert len(form_data.forum_groups) == 0
        assert len(form_data.sort_options) == 0
        assert len(form_data.sort_directions) == 0
        assert len(form_data.time_filter_options) == 0
        assert form_data.forum_field_name == "f[]"
    
    def test_parse_forum_field_name(self, mock_html_search_form):
        """Тест извлечения имени поля формы."""
        parser = SearchFormParser()
        form_data = parser.parse(mock_html_search_form)
        
        assert form_data.forum_field_name == "f[]"
    
    def test_parse_parent_id_extraction(self, mock_html_search_form):
        """Тест извлечения parent_id из классов."""
        parser = SearchFormParser()
        form_data = parser.parse(mock_html_search_form)
        
        all_sections = []
        for group in form_data.forum_groups:
            all_sections.extend(group.sections)
        
        sections_with_parent = [s for s in all_sections if s.parent_id is not None]
        if sections_with_parent:
            assert sections_with_parent[0].parent_id == 1
    
    def test_parse_selected_options(self, mock_html_search_form):
        """Тест определения выбранных опций."""
        parser = SearchFormParser()
        form_data = parser.parse(mock_html_search_form)
        
        selected_sort = next((o for o in form_data.sort_options if o.is_selected), None)
        assert selected_sort is not None
        
        selected_direction = next((d for d in form_data.sort_directions if d.is_selected), None)
        assert selected_direction is not None
        
        selected_time = next((t for t in form_data.time_filter_options if t.is_selected), None)
        assert selected_time is not None
    
    def test_parse_direct_options(self):
        """Тест парсинга прямых опций (не в optgroup)."""
        html = """
        <html>
        <body>
            <form>
                <select id="fs-main" name="f[]">
                    <option value="1" class="root_forum">Direct Option 1</option>
                    <option value="2">Direct Option 2</option>
                </select>
            </form>
        </body>
        </html>
        """
        parser = SearchFormParser()
        form_data = parser.parse(html)
        
        assert len(form_data.forum_groups) > 0

