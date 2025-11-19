from py_rutracker.models.search_form import (ForumGroup, ForumSection,
                                             SearchFormData, SortDirection,
                                             SortOption, TimeFilterOption)


class TestForumSection:
    """Тесты для модели ForumSection."""
    
    def test_create_forum_section(self):
        """Тест создания раздела форума."""
        section = ForumSection(
            id=1,
            name="Фильмы HD",
            parent_id=None,
            is_root=True,
            has_subforums=False
        )
        assert section.id == 1
        assert section.name == "Фильмы HD"
        assert section.parent_id is None
        assert section.is_root is True
        assert section.has_subforums is False
    
    def test_forum_section_with_parent(self):
        """Тест раздела с родителем."""
        section = ForumSection(
            id=2,
            name="Фильмы SD",
            parent_id=1,
            is_root=False,
            has_subforums=True
        )
        assert section.parent_id == 1
        assert section.is_root is False
        assert section.has_subforums is True
    
    def test_forum_section_defaults(self):
        """Тест значений по умолчанию."""
        section = ForumSection(id=1, name="Test")
        assert section.is_root is False
        assert section.has_subforums is False
        assert section.parent_id is None


class TestForumGroup:
    """Тесты для модели ForumGroup."""
    
    def test_create_forum_group(self):
        """Тест создания группы разделов."""
        sections = [
            ForumSection(id=1, name="Section 1"),
            ForumSection(id=2, name="Section 2")
        ]
        group = ForumGroup(name="Фильмы", sections=sections)
        assert group.name == "Фильмы"
        assert len(group.sections) == 2
        assert group.sections[0].id == 1
    
    def test_forum_group_empty_sections(self):
        """Тест группы с пустым списком разделов."""
        group = ForumGroup(name="Empty Group")
        assert group.name == "Empty Group"
        assert len(group.sections) == 0


class TestSortOption:
    """Тесты для модели SortOption."""
    
    def test_create_sort_option(self):
        """Тест создания опции сортировки."""
        option = SortOption(
            value=1,
            name="По дате",
            form_field_name="o",
            is_selected=True
        )
        assert option.value == 1
        assert option.name == "По дате"
        assert option.form_field_name == "o"
        assert option.is_selected is True
    
    def test_sort_option_defaults(self):
        """Тест значений по умолчанию."""
        option = SortOption(value=1, name="Test")
        assert option.form_field_name == "o"
        assert option.is_selected is False


class TestSortDirection:
    """Тесты для модели SortDirection."""
    
    def test_create_sort_direction(self):
        """Тест создания направления сортировки."""
        direction = SortDirection(
            value=1,
            name="По возрастанию",
            form_field_name="s",
            is_selected=True
        )
        assert direction.value == 1
        assert direction.name == "По возрастанию"
        assert direction.form_field_name == "s"
        assert direction.is_selected is True
    
    def test_sort_direction_defaults(self):
        """Тест значений по умолчанию."""
        direction = SortDirection(value=1, name="Test")
        assert direction.form_field_name == "s"
        assert direction.is_selected is False


class TestTimeFilterOption:
    """Тесты для модели TimeFilterOption."""
    
    def test_create_time_filter_option(self):
        """Тест создания опции фильтра по времени."""
        option = TimeFilterOption(
            value=0,
            name="За все время",
            form_field_name="tm",
            is_selected=True
        )
        assert option.value == 0
        assert option.name == "За все время"
        assert option.form_field_name == "tm"
        assert option.is_selected is True
    
    def test_time_filter_option_defaults(self):
        """Тест значений по умолчанию."""
        option = TimeFilterOption(value=0, name="Test")
        assert option.form_field_name == "tm"
        assert option.is_selected is False


class TestSearchFormData:
    """Тесты для модели SearchFormData."""
    
    def test_create_search_form_data(self):
        """Тест создания данных формы поиска."""
        forum_groups = [
            ForumGroup(name="Фильмы", sections=[
                ForumSection(id=1, name="Фильмы HD")
            ])
        ]
        sort_options = [
            SortOption(value=1, name="По дате")
        ]
        sort_directions = [
            SortDirection(value=1, name="По возрастанию")
        ]
        time_filters = [
            TimeFilterOption(value=0, name="За все время")
        ]
        
        form_data = SearchFormData(
            forum_groups=forum_groups,
            sort_options=sort_options,
            sort_directions=sort_directions,
            time_filter_options=time_filters,
            forum_field_name="f[]"
        )
        
        assert len(form_data.forum_groups) == 1
        assert len(form_data.sort_options) == 1
        assert len(form_data.sort_directions) == 1
        assert len(form_data.time_filter_options) == 1
        assert form_data.forum_field_name == "f[]"
    
    def test_search_form_data_defaults(self):
        """Тест значений по умолчанию."""
        form_data = SearchFormData()
        assert len(form_data.forum_groups) == 0
        assert len(form_data.sort_options) == 0
        assert len(form_data.sort_directions) == 0
        assert len(form_data.time_filter_options) == 0
        assert form_data.forum_field_name == "f[]"

