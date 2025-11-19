"""
Парсер для формы поиска RuTracker.
"""

from bs4 import BeautifulSoup

from ..models.search_form import (
    ForumGroup,
    ForumSection,
    SearchFormData,
    SortDirection,
    SortOption,
    TimeFilterOption,
)


class SearchFormParser:
    """
    Парсер для извлечения данных из формы поиска RuTracker.
    """

    @staticmethod
    def parse(html: str) -> SearchFormData:
        """
        Парсит HTML форму поиска и возвращает структурированные данные.

        :param html: HTML содержимое формы поиска.
        :return: Объект SearchFormData с данными формы.
        """
        soup = BeautifulSoup(html, features="lxml")
        forum_groups, forum_field_name = SearchFormParser._parse_forum_groups(soup)
        sort_options = SearchFormParser._parse_sort_options(soup)
        sort_directions = SearchFormParser._parse_sort_directions(soup)
        time_filter_options = SearchFormParser._parse_time_filters(soup)

        return SearchFormData(
            forum_groups=forum_groups,
            sort_options=sort_options,
            sort_directions=sort_directions,
            time_filter_options=time_filter_options,
            forum_field_name=forum_field_name,
        )

    @staticmethod
    def _parse_forum_groups(soup: BeautifulSoup) -> tuple[list[ForumGroup], str]:
        """
        Парсит группы разделов форума из формы поиска.

        :param soup: BeautifulSoup объект с HTML.
        :return: Кортеж (список групп разделов, имя поля формы).
        """
        forum_groups = []
        forum_field_name = "f[]"  # Значение по умолчанию

        select = soup.find("select", id="fs-main")
        if not select:
            return forum_groups, forum_field_name

        forum_field_name = select.get("name", "f[]")

        direct_options = select.find_all("option", recursive=False)
        for option in direct_options:
            if option.find_parent("optgroup"):
                continue

            value = option.get("value")
            if value is None:
                continue

            try:
                section_id = int(value)
            except ValueError:
                continue

            name = option.get_text(strip=True)
            classes = option.get("class", [])
            is_root = "root_forum" in classes
            has_subforums = "has_sf" in classes

            forum_groups.append(
                ForumGroup(
                    name="Общие",
                    sections=[
                        ForumSection(
                            id=section_id,
                            name=name,
                            parent_id=None,
                            is_root=is_root,
                            has_subforums=has_subforums,
                        )
                    ],
                )
            )

        optgroups = select.find_all("optgroup")

        for optgroup in optgroups:
            group_label = optgroup.get("label", "").strip()
            if not group_label:
                continue

            sections = []
            options = optgroup.find_all("option")

            for option in options:
                value = option.get("value")
                if value is None:
                    continue

                try:
                    section_id = int(value)
                except ValueError:
                    continue

                name = option.get_text(strip=True)

                parent_id = None
                classes = option.get("class", [])
                for cls in classes:
                    if cls.startswith("fp-"):
                        try:
                            parent_id = int(cls.replace("fp-", ""))
                            break
                        except ValueError:
                            continue

                is_root = "root_forum" in classes

                has_subforums = "has_sf" in classes

                sections.append(
                    ForumSection(
                        id=section_id,
                        name=name,
                        parent_id=parent_id,
                        is_root=is_root,
                        has_subforums=has_subforums,
                    )
                )

            if sections:
                forum_groups.append(ForumGroup(name=group_label, sections=sections))

        return forum_groups, forum_field_name

    @staticmethod
    def _parse_sort_options(soup: BeautifulSoup) -> list[SortOption]:
        """
        Парсит опции сортировки из формы поиска.

        :param soup: BeautifulSoup объект с HTML.
        :return: Список опций сортировки.
        """
        sort_options = []

        select = soup.find("select", attrs={"name": "o"})
        if not select:
            return sort_options

        form_field_name = select.get("name", "o")

        options = select.find_all("option")

        for option in options:
            value = option.get("value")
            if value is None:
                continue

            try:
                option_value = int(value)
            except ValueError:
                continue

            name = option.get_text(strip=True)
            is_selected = option.get("selected") is not None

            sort_options.append(
                SortOption(
                    value=option_value,
                    name=name,
                    form_field_name=form_field_name,
                    is_selected=is_selected,
                )
            )

        return sort_options

    @staticmethod
    def _parse_sort_directions(soup: BeautifulSoup) -> list[SortDirection]:
        """
        Парсит направления сортировки из формы поиска.

        :param soup: BeautifulSoup объект с HTML.
        :return: Список направлений сортировки.
        """
        sort_directions = []

        radio_inputs = soup.find_all("input", attrs={"type": "radio", "name": "s"})

        if radio_inputs:
            form_field_name = radio_inputs[0].get("name", "s")
        else:
            form_field_name = "s"

        for radio in radio_inputs:
            value = radio.get("value")
            if value is None:
                continue

            try:
                direction_value = int(value)
            except ValueError:
                continue

            label = radio.find_parent("label")
            if label:
                name = label.get_text(strip=True)
            else:
                name = "по возрастанию" if direction_value == 1 else "по убыванию"

            is_selected = radio.get("checked") is not None

            sort_directions.append(
                SortDirection(
                    value=direction_value,
                    name=name,
                    form_field_name=form_field_name,
                    is_selected=is_selected,
                )
            )

        return sort_directions

    @staticmethod
    def _parse_time_filters(soup: BeautifulSoup) -> list[TimeFilterOption]:
        """
        Парсит фильтры по времени из формы поиска.

        :param soup: BeautifulSoup объект с HTML.
        :return: Список опций фильтра по времени.
        """
        time_filters = []

        select = soup.find("select", attrs={"name": "tm"})
        if not select:
            return time_filters

        form_field_name = select.get("name", "tm")

        options = select.find_all("option")

        for option in options:
            value = option.get("value")
            if value is None:
                continue

            try:
                filter_value = int(value)
            except ValueError:
                continue

            name = option.get_text(strip=True)
            is_selected = option.get("selected") is not None

            time_filters.append(
                TimeFilterOption(
                    value=filter_value,
                    name=name,
                    form_field_name=form_field_name,
                    is_selected=is_selected,
                )
            )

        return time_filters
