"""
Пример использования метода get_search_form для получения формы поиска RuTracker (асинхронный клиент).
"""

import os
import sys
import asyncio
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
PROXY = os.getenv("PROXY", None)  #'http://<PROXY_IP_ADDRESS>:<PROXY_PORT>'  Опционально

from py_rutracker.clients.async_client import AsyncRuTrackerClient


async def main():
    async with AsyncRuTrackerClient(
        LOGIN, PASSWORD, PROXY
    ) as client:
        # Получить форму поиска (будет закеширована на 24 часа)
        form_data = await client.get_search_form()

        print(f"Найдено групп разделов: {len(form_data.forum_groups)}")
        print(f"Найдено опций сортировки: {len(form_data.sort_options)}")
        print(f"Найдено направлений сортировки: {len(form_data.sort_directions)}")
        print(f"Найдено фильтров по времени: {len(form_data.time_filter_options)}\n")

        # Показываем первые несколько групп разделов
        print("Примеры групп разделов:")
        for i, group in enumerate(form_data.forum_groups[:3], 1):
            print(f"\n{i}. {group.name} ({len(group.sections)} разделов)")
            for section in group.sections[:3]:
                indent = "  " if section.parent_id else ""
                print(f"   {indent}- [{section.id}] {section.name}")
                if section.has_subforums:
                    print(f"     (есть подразделы)")

        # Показываем опции сортировки
        print("\n\nОпции сортировки:")
        for option in form_data.sort_options:
            selected = "✓" if option.is_selected else " "
            print(f"  [{selected}] {option.value}: {option.name}")

        # Показываем направления сортировки
        print("\n\nНаправления сортировки:")
        for direction in form_data.sort_directions:
            selected = "✓" if direction.is_selected else " "
            print(f"  [{selected}] {direction.value}: {direction.name}")

        # Показываем фильтры по времени
        print("\n\nФильтры по времени:")
        for time_filter in form_data.time_filter_options:
            selected = "✓" if time_filter.is_selected else " "
            print(f"  [{selected}] {time_filter.value}: {time_filter.name}")

        # Второй вызов - данные будут взяты из кеша
        print("\n\nВторой вызов get_search_form() - данные из кеша:")
        form_data_cached = await client.get_search_form()
        print(f"Данные получены из кеша: {form_data_cached == form_data}")

        # Принудительное обновление кеша
        print("\n\nПринудительное обновление кеша:")
        form_data_refreshed = await client.get_search_form(force_refresh=True)
        print(f"Кеш обновлен, получено групп: {len(form_data_refreshed.forum_groups)}")


if __name__ == "__main__":
    asyncio.run(main())
