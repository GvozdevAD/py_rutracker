from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field


class ForumSection(BaseModel):
    """
    Модель для раздела форума.

    :param id: Идентификатор раздела (value из option, может быть -1 для "Все имеющиеся").
    :param name: Название раздела.
    :param parent_id: ID родительского раздела (если есть, извлекается из class="fp-{parent_id}").
    :param is_root: Является ли раздел корневым (есть class="root_forum").
    :param has_subforums: Есть ли у раздела подразделы (есть class="has_sf").
    """

    id: int = Field(..., description="Идентификатор раздела")
    name: str = Field(..., description="Название раздела")
    parent_id: Optional[int] = Field(None, description="ID родительского раздела")
    is_root: bool = Field(default=False, description="Является ли раздел корневым")
    has_subforums: bool = Field(
        default=False, description="Есть ли у раздела подразделы"
    )

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)


class ForumGroup(BaseModel):
    """
    Модель для группы разделов форума.

    :param name: Название группы (label из optgroup).
    :param sections: Список разделов в группе.
    """

    name: str = Field(..., description="Название группы разделов")
    sections: List[ForumSection] = Field(
        default_factory=list, description="Список разделов в группе"
    )

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)


class SortOption(BaseModel):
    """
    Модель для опции сортировки.

    :param value: Значение опции (value из option).
    :param name: Название опции.
    :param form_field_name: Имя поля формы для POST-запроса (name из select).
    :param is_selected: Выбрана ли опция по умолчанию.
    """

    value: int = Field(..., description="Значение опции сортировки")
    name: str = Field(..., description="Название опции сортировки")
    form_field_name: str = Field(
        default="o", description="Имя поля формы для POST-запроса"
    )
    is_selected: bool = Field(
        default=False, description="Выбрана ли опция по умолчанию"
    )

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)


class SortDirection(BaseModel):
    """
    Модель для направления сортировки.

    :param value: Значение направления (1 - по возрастанию, 2 - по убыванию).
    :param name: Название направления.
    :param form_field_name: Имя поля формы для POST-запроса (name из input).
    :param is_selected: Выбрано ли направление по умолчанию.
    """

    value: int = Field(
        ...,
        description="Значение направления сортировки (1 - возрастание, 2 - убывание)",
    )
    name: str = Field(..., description="Название направления сортировки")
    form_field_name: str = Field(
        default="s", description="Имя поля формы для POST-запроса"
    )
    is_selected: bool = Field(
        default=False, description="Выбрано ли направление по умолчанию"
    )

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)


class TimeFilterOption(BaseModel):
    """
    Модель для опции фильтра по времени.

    :param value: Значение опции (value из option).
    :param name: Название опции.
    :param form_field_name: Имя поля формы для POST-запроса (name из select).
    :param is_selected: Выбрана ли опция по умолчанию.
    """

    value: int = Field(..., description="Значение фильтра по времени")
    name: str = Field(..., description="Название фильтра по времени")
    form_field_name: str = Field(
        default="tm", description="Имя поля формы для POST-запроса"
    )
    is_selected: bool = Field(
        default=False, description="Выбрана ли опция по умолчанию"
    )

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)


class SearchFormData(BaseModel):
    """
    Модель для всех данных формы поиска RuTracker.

    :param forum_groups: Список групп разделов форума.
    :param sort_options: Список опций сортировки.
    :param sort_directions: Список направлений сортировки.
    :param time_filter_options: Список опций фильтра по времени.
    :param forum_field_name: Имя поля формы для разделов форума (по умолчанию "f[]").
    """

    forum_groups: List[ForumGroup] = Field(
        default_factory=list, description="Группы разделов форума"
    )
    sort_options: List[SortOption] = Field(
        default_factory=list, description="Опции сортировки"
    )
    sort_directions: List[SortDirection] = Field(
        default_factory=list, description="Направления сортировки"
    )
    time_filter_options: List[TimeFilterOption] = Field(
        default_factory=list, description="Опции фильтра по времени"
    )
    forum_field_name: str = Field(
        default="f[]", description="Имя поля формы для разделов форума"
    )

    model_config = ConfigDict(use_enum_values=True, validate_assignment=True)
    
    def get_sort_option_by_name(self, name: str) -> Optional[SortOption]:
        """
        Находит опцию сортировки по названию (частичное совпадение, регистронезависимо).
        
        :param name: Название опции сортировки (например, "дате", "размеру", "скачиваниям").
        :return: Объект SortOption или None, если не найдено.
        """
        name_lower = name.lower()
        for option in self.sort_options:
            if name_lower in option.name.lower():
                return option
        return None
    
    def get_sort_option_by_value(self, value: int) -> Optional[SortOption]:
        """
        Находит опцию сортировки по значению.
        
        :param value: Значение опции сортировки.
        :return: Объект SortOption или None, если не найдено.
        """
        return next((opt for opt in self.sort_options if opt.value == value), None)
    
    def get_sort_direction_by_name(self, name: str) -> Optional[SortDirection]:
        """
        Находит направление сортировки по названию (частичное совпадение, регистронезависимо).
        
        :param name: Название направления (например, "возрастанию", "убыванию").
        :return: Объект SortDirection или None, если не найдено.
        """
        name_lower = name.lower()
        for direction in self.sort_directions:
            if name_lower in direction.name.lower():
                return direction
        return None
    
    def get_time_filter_by_name(self, name: str) -> Optional[TimeFilterOption]:
        """
        Находит фильтр по времени по названию (частичное совпадение, регистронезависимо).
        
        :param name: Название фильтра (например, "7 дней", "месяц", "год").
        :return: Объект TimeFilterOption или None, если не найдено.
        """
        name_lower = name.lower()
        for time_filter in self.time_filter_options:
            if name_lower in time_filter.name.lower():
                return time_filter
        return None
    
    def get_time_filter_by_value(self, value: int) -> Optional[TimeFilterOption]:
        """
        Находит фильтр по времени по значению.
        
        :param value: Значение фильтра по времени.
        :return: Объект TimeFilterOption или None, если не найдено.
        """
        return next((tf for tf in self.time_filter_options if tf.value == value), None)
    
    def get_forum_ids_by_name(self, name: str) -> List[int]:
        """
        Находит ID форумов по названию раздела (частичное совпадение, регистронезависимо).
        Может вернуть несколько ID, если найдено несколько совпадений.
        
        :param name: Название раздела форума (например, "Музыка", "Фильмы", "Игры").
        :return: Список ID форумов.
        """
        forum_ids = []
        name_lower = name.lower()
        for group in self.forum_groups:
            for section in group.sections:
                if name_lower in section.name.lower():
                    forum_ids.append(section.id)
        return forum_ids
    
    def get_forum_ids_by_group_name(self, group_name: str) -> List[int]:
        """
        Находит ID всех форумов в группе по названию группы (частичное совпадение, регистронезависимо).
        
        :param group_name: Название группы разделов (например, "Музыка", "Видео", "Игры").
        :return: Список ID форумов в группе.
        """
        group_name_lower = group_name.lower()
        for group in self.forum_groups:
            if group_name_lower in group.name.lower():
                return [section.id for section in group.sections]
        return []
    
    @property
    def default_sort_option(self) -> Optional[SortOption]:
        """
        Возвращает выбранную опцию сортировки по умолчанию.
        
        :return: Объект SortOption или None, если ничего не выбрано.
        """
        return next((opt for opt in self.sort_options if opt.is_selected), None)
    
    @property
    def default_sort_direction(self) -> Optional[SortDirection]:
        """
        Возвращает выбранное направление сортировки по умолчанию.
        
        :return: Объект SortDirection или None, если ничего не выбрано.
        """
        return next((d for d in self.sort_directions if d.is_selected), None)
    
    @property
    def default_time_filter(self) -> Optional[TimeFilterOption]:
        """
        Возвращает выбранный фильтр по времени по умолчанию.
        
        :return: Объект TimeFilterOption или None, если ничего не выбрано.
        """
        return next((tf for tf in self.time_filter_options if tf.is_selected), None)