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
