"""
Пример использования вспомогательных методов SearchFormData для удобного поиска значений.
Демонстрирует работу с формой поиска без необходимости проходить по спискам вручную.
"""

import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
PROXY = os.getenv("PROXY", None)  # 'http://<PROXY_IP_ADDRESS>:<PROXY_PORT>'  Опционально

from py_rutracker import RuTrackerClient

# Создание клиента с вашими учетными данными
client = RuTrackerClient(LOGIN, PASSWORD, PROXY)

try:
    # Получить форму поиска
    form_data = client.get_search_form()

    print("=" * 60)
    print("ИСПОЛЬЗОВАНИЕ ВСПОМОГАТЕЛЬНЫХ МЕТОДОВ SearchFormData")
    print("=" * 60)

    # 1. Использование значений по умолчанию
    print("\n1. Значения по умолчанию из формы:")
    print("-" * 60)
    
    if form_data.default_sort_option:
        print(f"Опция сортировки по умолчанию: {form_data.default_sort_option.value} - {form_data.default_sort_option.name}")
    
    if form_data.default_sort_direction:
        print(f"Направление сортировки по умолчанию: {form_data.default_sort_direction.value} - {form_data.default_sort_direction.name}")
    
    if form_data.default_time_filter:
        print(f"Фильтр по времени по умолчанию: {form_data.default_time_filter.value} - {form_data.default_time_filter.name}")

    # 2. Поиск опции сортировки по названию
    print("\n2. Поиск опции сортировки по названию:")
    print("-" * 60)
    
    # Поиск по частичному совпадению (регистронезависимо)
    sort_option = form_data.get_sort_option_by_name("дате")
    if sort_option:
        print(f"Найдена опция: '{sort_option.name}' (value={sort_option.value})")
    
    sort_option = form_data.get_sort_option_by_name("размеру")
    if sort_option:
        print(f"Найдена опция: '{sort_option.name}' (value={sort_option.value})")
    
    sort_option = form_data.get_sort_option_by_name("скачиваний")
    if sort_option:
        print(f"Найдена опция: '{sort_option.name}' (value={sort_option.value})")

    # 3. Поиск направления сортировки по названию
    print("\n3. Поиск направления сортировки по названию:")
    print("-" * 60)
    
    sort_direction = form_data.get_sort_direction_by_name("возрастанию")
    if sort_direction:
        print(f"Найдено направление: '{sort_direction.name}' (value={sort_direction.value})")
    
    sort_direction = form_data.get_sort_direction_by_name("убыванию")
    if sort_direction:
        print(f"Найдено направление: '{sort_direction.name}' (value={sort_direction.value})")

    # 4. Поиск фильтра по времени по названию
    print("\n4. Поиск фильтра по времени по названию:")
    print("-" * 60)
    
    time_filter = form_data.get_time_filter_by_name("7 дней")
    if time_filter:
        print(f"Найден фильтр: '{time_filter.name}' (value={time_filter.value})")
    
    time_filter = form_data.get_time_filter_by_name("месяц")
    if time_filter:
        print(f"Найден фильтр: '{time_filter.name}' (value={time_filter.value})")

    # 5. Поиск форумов по названию группы
    print("\n5. Поиск форумов по названию группы:")
    print("-" * 60)
    
    music_forums = form_data.get_forum_ids_by_group_name("Музыка")
    if music_forums:
        print(f"Найдено форумов в группе 'Музыка': {len(music_forums)}")
        print(f"Первые 5 ID: {music_forums[:5]}")
    
    film_forums = form_data.get_forum_ids_by_group_name("Фильмы")
    if film_forums:
        print(f"Найдено форумов в группе 'Фильмы': {len(film_forums)}")
        print(f"Первые 5 ID: {film_forums[:5]}")

    # 6. Поиск форумов по названию раздела
    print("\n6. Поиск форумов по названию раздела:")
    print("-" * 60)
    
    forums = form_data.get_forum_ids_by_name("HD")
    if forums:
        print(f"Найдено форумов с 'HD' в названии: {len(forums)}")
        print(f"ID: {forums[:10]}")  # Показываем первые 10

    # 7. Практическое применение: поиск с использованием найденных значений
    print("\n7. Практическое применение:")
    print("-" * 60)
    
    # Находим опцию сортировки по дате
    sort_by_date = form_data.get_sort_option_by_name("дате")
    # Находим направление по убыванию
    sort_desc = form_data.get_sort_direction_by_name("убыванию")
    
    if sort_by_date and sort_desc:
        print(f"Выполняем поиск с сортировкой: {sort_by_date.name}, {sort_desc.name}")
        results = client.search_with_form(
            "Static-X",
            sort_option=sort_by_date.value,
            sort_direction=sort_desc.value,
            page=1  # Первая страница
        )
        print(f"Найдено результатов: {len(results)}")
        if results:
            print(f"Первый результат: {results[0].title}")

    # Поиск в конкретных форумах
    if music_forums:
        print(f"\nПоиск в музыкальных форумах (первые 3 форума):")
        results = client.search_with_form(
            "Static-X",
            forum_ids=music_forums[:3],
            page=1
        )
        print(f"Найдено результатов: {len(results)}")

    # 8. Использование значений по умолчанию для поиска
    print("\n8. Поиск с использованием значений по умолчанию:")
    print("-" * 60)
    
    if form_data.default_sort_option and form_data.default_sort_direction:
        print(f"Используем значения по умолчанию:")
        print(f"  Сортировка: {form_data.default_sort_option.name}")
        print(f"  Направление: {form_data.default_sort_direction.name}")
        
        results = client.search_with_form(
            "Static-X",
            sort_option=form_data.default_sort_option.value,
            sort_direction=form_data.default_sort_direction.value,
            page=1
        )
        print(f"Найдено результатов: {len(results)}")

    print("\n" + "=" * 60)
    print("Пример завершен!")
    print("=" * 60)

finally:
    # Закрытие сессии
    client.__exit__(None, None, None)

