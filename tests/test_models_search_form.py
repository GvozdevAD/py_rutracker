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
    
    def test_get_sort_option_by_name(self):
        """Тест поиска опции сортировки по названию."""
        sort_options = [
            SortOption(value=10, name="По дате добавления"),
            SortOption(value=7, name="По размеру"),
            SortOption(value=8, name="По количеству скачиваний")
        ]
        form_data = SearchFormData(sort_options=sort_options)
        
        option = form_data.get_sort_option_by_name("дате")
        assert option is not None
        assert option.value == 10
        
        option = form_data.get_sort_option_by_name("размеру")
        assert option is not None
        assert option.value == 7
        
        option = form_data.get_sort_option_by_name("скачиваний")
        assert option is not None
        assert option.value == 8
        
        option = form_data.get_sort_option_by_name("несуществующая")
        assert option is None
    
    def test_get_sort_option_by_value(self):
        """Тест поиска опции сортировки по значению."""
        sort_options = [
            SortOption(value=10, name="По дате"),
            SortOption(value=7, name="По размеру")
        ]
        form_data = SearchFormData(sort_options=sort_options)
        
        option = form_data.get_sort_option_by_value(10)
        assert option is not None
        assert option.name == "По дате"
        
        option = form_data.get_sort_option_by_value(999)
        assert option is None
    
    def test_get_sort_direction_by_name(self):
        """Тест поиска направления сортировки по названию."""
        sort_directions = [
            SortDirection(value=1, name="По возрастанию"),
            SortDirection(value=2, name="По убыванию")
        ]
        form_data = SearchFormData(sort_directions=sort_directions)
        
        direction = form_data.get_sort_direction_by_name("возрастанию")
        assert direction is not None
        assert direction.value == 1
        
        direction = form_data.get_sort_direction_by_name("убыванию")
        assert direction is not None
        assert direction.value == 2
        
        direction = form_data.get_sort_direction_by_name("несуществующее")
        assert direction is None
    
    def test_get_time_filter_by_name(self):
        """Тест поиска фильтра по времени по названию."""
        time_filters = [
            TimeFilterOption(value=0, name="За все время"),
            TimeFilterOption(value=7, name="За последние 7 дней"),
            TimeFilterOption(value=30, name="За последние 30 дней")
        ]
        form_data = SearchFormData(time_filter_options=time_filters)
        
        time_filter = form_data.get_time_filter_by_name("7 дней")
        assert time_filter is not None
        assert time_filter.value == 7
        
        time_filter = form_data.get_time_filter_by_name("30 дней")
        assert time_filter is not None
        assert time_filter.value == 30
        
        time_filter = form_data.get_time_filter_by_name("несуществующий")
        assert time_filter is None
    
    def test_get_time_filter_by_value(self):
        """Тест поиска фильтра по времени по значению."""
        time_filters = [
            TimeFilterOption(value=7, name="За последние 7 дней"),
            TimeFilterOption(value=30, name="За последние 30 дней")
        ]
        form_data = SearchFormData(time_filter_options=time_filters)
        
        time_filter = form_data.get_time_filter_by_value(7)
        assert time_filter is not None
        assert time_filter.name == "За последние 7 дней"
        
        time_filter = form_data.get_time_filter_by_value(999)
        assert time_filter is None
    
    def test_get_forum_ids_by_name(self):
        """Тест поиска ID форумов по названию."""
        forum_groups = [
            ForumGroup(name="Фильмы", sections=[
                ForumSection(id=1, name="Фильмы HD"),
                ForumSection(id=2, name="Фильмы SD")
            ]),
            ForumGroup(name="Музыка", sections=[
                ForumSection(id=10, name="Музыка Lossless"),
                ForumSection(id=11, name="Музыка MP3")
            ])
        ]
        form_data = SearchFormData(forum_groups=forum_groups)
        
        forum_ids = form_data.get_forum_ids_by_name("HD")
        assert len(forum_ids) == 1
        assert 1 in forum_ids
        
        forum_ids = form_data.get_forum_ids_by_name("Фильмы")
        assert len(forum_ids) == 2
        assert 1 in forum_ids
        assert 2 in forum_ids
        
        forum_ids = form_data.get_forum_ids_by_name("музыка")
        assert len(forum_ids) == 2
        assert 10 in forum_ids
        assert 11 in forum_ids
        
        forum_ids = form_data.get_forum_ids_by_name("несуществующий")
        assert len(forum_ids) == 0
    
    def test_get_forum_ids_by_group_name(self):
        """Тест поиска ID форумов по названию группы."""
        forum_groups = [
            ForumGroup(name="Фильмы", sections=[
                ForumSection(id=1, name="Фильмы HD"),
                ForumSection(id=2, name="Фильмы SD")
            ]),
            ForumGroup(name="Музыка", sections=[
                ForumSection(id=10, name="Музыка Lossless"),
                ForumSection(id=11, name="Музыка MP3")
            ])
        ]
        form_data = SearchFormData(forum_groups=forum_groups)
        
        forum_ids = form_data.get_forum_ids_by_group_name("Фильмы")
        assert len(forum_ids) == 2
        assert 1 in forum_ids
        assert 2 in forum_ids
        
        forum_ids = form_data.get_forum_ids_by_group_name("музыка")
        assert len(forum_ids) == 2
        assert 10 in forum_ids
        assert 11 in forum_ids
        
        forum_ids = form_data.get_forum_ids_by_group_name("Фильм")
        assert len(forum_ids) == 2
        
        forum_ids = form_data.get_forum_ids_by_group_name("несуществующая")
        assert len(forum_ids) == 0
    
    def test_default_sort_option(self):
        """Тест получения опции сортировки по умолчанию."""
        sort_options = [
            SortOption(value=1, name="По дате", is_selected=False),
            SortOption(value=10, name="По дате добавления", is_selected=True),
            SortOption(value=7, name="По размеру", is_selected=False)
        ]
        form_data = SearchFormData(sort_options=sort_options)
        
        default_option = form_data.default_sort_option
        assert default_option is not None
        assert default_option.value == 10
        assert default_option.is_selected is True
    
    def test_default_sort_option_none(self):
        """Тест получения опции сортировки по умолчанию, когда ничего не выбрано."""
        sort_options = [
            SortOption(value=1, name="По дате", is_selected=False),
            SortOption(value=10, name="По дате добавления", is_selected=False)
        ]
        form_data = SearchFormData(sort_options=sort_options)
        
        default_option = form_data.default_sort_option
        assert default_option is None
    
    def test_default_sort_direction(self):
        """Тест получения направления сортировки по умолчанию."""
        sort_directions = [
            SortDirection(value=1, name="По возрастанию", is_selected=False),
            SortDirection(value=2, name="По убыванию", is_selected=True)
        ]
        form_data = SearchFormData(sort_directions=sort_directions)
        
        default_direction = form_data.default_sort_direction
        assert default_direction is not None
        assert default_direction.value == 2
        assert default_direction.is_selected is True
    
    def test_default_sort_direction_none(self):
        """Тест получения направления сортировки по умолчанию, когда ничего не выбрано."""
        sort_directions = [
            SortDirection(value=1, name="По возрастанию", is_selected=False),
            SortDirection(value=2, name="По убыванию", is_selected=False)
        ]
        form_data = SearchFormData(sort_directions=sort_directions)
        
        default_direction = form_data.default_sort_direction
        assert default_direction is None
    
    def test_default_time_filter(self):
        """Тест получения фильтра по времени по умолчанию."""
        time_filters = [
            TimeFilterOption(value=0, name="За все время", is_selected=False),
            TimeFilterOption(value=7, name="За последние 7 дней", is_selected=True)
        ]
        form_data = SearchFormData(time_filter_options=time_filters)
        
        default_filter = form_data.default_time_filter
        assert default_filter is not None
        assert default_filter.value == 7
        assert default_filter.is_selected is True
    
    def test_default_time_filter_none(self):
        """Тест получения фильтра по времени по умолчанию, когда ничего не выбрано."""
        time_filters = [
            TimeFilterOption(value=0, name="За все время", is_selected=False),
            TimeFilterOption(value=7, name="За последние 7 дней", is_selected=False)
        ]
        form_data = SearchFormData(time_filter_options=time_filters)
        
        default_filter = form_data.default_time_filter
        assert default_filter is None
