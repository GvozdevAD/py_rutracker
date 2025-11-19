"""
Пример продвинутого использования поиска через форму с использованием вспомогательных методов SearchFormData.
Демонстрирует комбинирование различных параметров поиска.
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

    print("=" * 70)
    print("ПРОДВИНУТЫЙ ПОИСК С ИСПОЛЬЗОВАНИЕМ ВСПОМОГАТЕЛЬНЫХ МЕТОДОВ")
    print("=" * 70)

    # Пример 1: Поиск с сортировкой по дате (новые раздачи первыми)
    print("\n1. Поиск новых раздач (сортировка по дате, по убыванию):")
    print("-" * 70)
    
    # Показываем доступные опции сортировки для отладки
    print("Доступные опции сортировки:")
    for opt in form_data.sort_options[:5]:  # Показываем первые 5
        print(f"  {opt.value}: {opt.name}")
    
    sort_by_date = form_data.get_sort_option_by_name("дате")
    sort_desc = form_data.get_sort_direction_by_name("убыванию")
    
    if sort_by_date:
        print(f"\nНайдена опция сортировки: {sort_by_date.name} (value={sort_by_date.value})")
    else:
        print("Опция сортировки по дате не найдена!")
        # Попробуем найти по значению (обычно 10 - по дате)
        sort_by_date = form_data.get_sort_option_by_value(10)
        if sort_by_date:
            print(f"Используем опцию по значению 10: {sort_by_date.name}")
    
    if sort_desc:
        print(f"Найдено направление: {sort_desc.name} (value={sort_desc.value})")
    else:
        print("Направление сортировки не найдено!")
        # По умолчанию используем 2 (по убыванию)
        sort_desc_value = 2
    
    if sort_by_date:
        sort_desc_value = sort_desc.value if sort_desc else 2
        # Поиск на первой странице
        results = client.search_with_form(
            "Rammstein",
            sort_option=sort_by_date.value,
            sort_direction=sort_desc_value,
            page=1
        )
        print(f"Найдено результатов: {len(results)}")
        if results:
            print("\nПоследние 5 раздач:")
            for result in results[:5]:
                print(f"  • {result.title}")
                print(f"    Добавлено: {result.added}, Размер: {result.size} {result.unit}")
        else:
            print("Результаты не найдены")
            # Попробуем без сортировки
            print("\nПробуем поиск без указания сортировки...")
            results = client.search_with_form("Rammstein", page=1)
            print(f"Найдено результатов без сортировки: {len(results)}")
    else:
        print("Не удалось найти опцию сортировки, пропускаем пример")

    # Пример 2: Поиск самых популярных раздач (по количеству скачиваний)
    print("\n2. Поиск популярных раздач (сортировка по скачиваниям):")
    print("-" * 70)
    
    sort_by_downloads = form_data.get_sort_option_by_name("скачиваний")
    if not sort_by_downloads:
        # Попробуем найти по другим вариантам названия
        sort_by_downloads = form_data.get_sort_option_by_name("скачивания")
    if not sort_by_downloads:
        # Попробуем по значению (обычно 8 - по скачиваниям)
        sort_by_downloads = form_data.get_sort_option_by_value(8)
    
    sort_desc_value = sort_desc.value if sort_desc else 2
    
    if sort_by_downloads:
        print(f"Используем опцию: {sort_by_downloads.name} (value={sort_by_downloads.value})")
        results = client.search_with_form(
            "Rammstein",
            sort_option=sort_by_downloads.value,
            sort_direction=sort_desc_value,
            page=1
        )
        print(f"Найдено результатов: {len(results)}")
        if results:
            print("\nТоп 5 по скачиваниям:")
            for result in results[:5]:
                print(f"  • {result.title}")
                print(f"    Скачиваний: {result.download_counter}, Размер: {result.size} {result.unit}")
        else:
            print("Результаты не найдены")
    else:
        print("Опция сортировки по скачиваниям не найдена, пропускаем пример")

    # Пример 3: Поиск в конкретных форумах с фильтром по времени
    print("\n3. Поиск в музыкальных форумах за последние 7 дней:")
    print("-" * 70)
    
    music_forums = form_data.get_forum_ids_by_group_name("Музыка")
    time_filter_7days = form_data.get_time_filter_by_name("7 дней")
    
    if not time_filter_7days:
        # Попробуем найти по значению (обычно 7 - за последние 7 дней)
        time_filter_7days = form_data.get_time_filter_by_value(7)
    
    if music_forums:
        print(f"Найдено музыкальных форумов: {len(music_forums)}")
    else:
        print("Музыкальные форумы не найдены!")
    
    if time_filter_7days:
        print(f"Найден фильтр по времени: {time_filter_7days.name} (value={time_filter_7days.value})")
    else:
        print("Фильтр по времени не найден!")
    
    if music_forums and time_filter_7days:
        sort_option_value = sort_by_date.value if sort_by_date else None
        sort_dir_value = sort_desc.value if sort_desc else 2
        
        results = client.search_with_form(
            "Rammstein",
            forum_ids=music_forums[:5],  # Первые 5 музыкальных форумов
            time_filter=time_filter_7days.value,
            sort_option=sort_option_value,
            sort_direction=sort_dir_value,
            page=1
        )
        print(f"Найдено результатов в музыкальных форумах за последние 7 дней: {len(results)}")
        if results:
            print("\nПримеры результатов:")
            for result in results[:3]:
                print(f"  • [{result.category}] {result.title}")
                print(f"    Добавлено: {result.added}")
        else:
            print("Результаты не найдены")
    else:
        print("Не удалось найти необходимые параметры, пропускаем пример")

    # Пример 4: Поиск больших раздач (сортировка по размеру)
    print("\n4. Поиск самых больших раздач (сортировка по размеру):")
    print("-" * 70)
    
    # Показываем все опции сортировки для отладки
    print("Все доступные опции сортировки:")
    for opt in form_data.sort_options:
        print(f"  {opt.value}: {opt.name}")
    
    sort_by_size = form_data.get_sort_option_by_name("размеру")
    if not sort_by_size:
        print("\nОпция 'размеру' не найдена по названию, пробуем другие варианты...")
        # Попробуем разные варианты поиска
        sort_by_size = form_data.get_sort_option_by_name("размер")
        if not sort_by_size:
            sort_by_size = form_data.get_sort_option_by_name("размера")
        if not sort_by_size:
            # Попробуем по значению (обычно 7 - по размеру)
            sort_by_size = form_data.get_sort_option_by_value(7)
            if sort_by_size:
                print(f"Найдено по значению 7: {sort_by_size.name}")
        else:
            print(f"Найдено по альтернативному названию: {sort_by_size.name}")
    
    sort_desc_value = sort_desc.value if sort_desc else 2
    
    if sort_by_size:
        print(f"\nИспользуем опцию: {sort_by_size.name} (value={sort_by_size.value})")
        print(f"Направление сортировки: {sort_desc_value}")
        
        # Сначала пробуем с сортировкой
        results = client.search_with_form(
            "Rammstein",
            sort_option=sort_by_size.value,
            sort_direction=sort_desc_value,
            page=1
        )
        print(f"Найдено результатов с сортировкой: {len(results)}")
        
        if not results:
            print("\nРезультаты пустые, пробуем без указания сортировки...")
            results = client.search_with_form("Rammstein", page=1)
            print(f"Найдено результатов без сортировки: {len(results)}")
            
            if results:
                print("\nРезультаты без сортировки (первые 5):")
                for result in results[:5]:
                    print(f"  • {result.title} - {result.size} {result.unit}")
        
        if results:
            print("\nТоп 5 по размеру:")
            # Сортируем результаты по размеру вручную, если они есть
            sorted_results = sorted(results, key=lambda x: (x.size, x.unit), reverse=True)
            for result in sorted_results[:5]:
                print(f"  • {result.title}")
                print(f"    Размер: {result.size} {result.unit}")
    else:
        print("Опция сортировки по размеру не найдена!")
        print("Пробуем поиск без сортировки...")
        results = client.search_with_form("Rammstein", page=1)
        print(f"Найдено результатов: {len(results)}")
        if results:
            print("\nРезультаты (первые 5):")
            for result in results[:5]:
                print(f"  • {result.title} - {result.size} {result.unit}")

    # Пример 5: Поиск с использованием значений по умолчанию из формы
    print("\n5. Поиск с настройками по умолчанию из формы:")
    print("-" * 70)
    
    if form_data.default_sort_option and form_data.default_sort_direction:
        print(f"Используем настройки по умолчанию:")
        print(f"  Сортировка: {form_data.default_sort_option.name}")
        print(f"  Направление: {form_data.default_sort_direction.name}")
        
        results = client.search_with_form(
            "Rammstein",
            sort_option=form_data.default_sort_option.value,
            sort_direction=form_data.default_sort_direction.value,
            page=1
        )
        print(f"Найдено результатов: {len(results)}")
        if results:
            print("\nПримеры результатов:")
            for result in results[:3]:
                print(f"  • {result.title}")
        else:
            print("Результаты не найдены")

    # Пример 6: Поиск по всем страницам с фильтрами
    print("\n6. Поиск по всем страницам с применением фильтров:")
    print("-" * 70)
    
    if sort_by_date and sort_desc:
        print("Выполняем поиск по всем страницам (максимум 3 страницы)...")
        all_results = client.search_all_pages_with_form(
            "Rammstein",
            max_pages=3,
            sort_option=sort_by_date.value,
            sort_direction=sort_desc.value
        )
        print(f"Всего найдено результатов на всех страницах: {len(all_results)}")
        
        if all_results:
            # Группировка по категориям
            categories = {}
            for result in all_results:
                if result.category not in categories:
                    categories[result.category] = []
                categories[result.category].append(result)
            
            print("\nРезультаты по категориям:")
            for category, results_list in sorted(categories.items()):
                print(f"  {category}: {len(results_list)} результатов")
        else:
            print("Результаты не найдены")

    print("\n" + "=" * 70)
    print("Пример завершен!")
    print("=" * 70)

finally:
    # Закрытие сессии
    client.__exit__(None, None, None)

