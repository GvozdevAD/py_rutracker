# Примеры использования

Подробные примеры использования библиотеки Py_RuTracker.

## Содержание

- [Быстрый старт](#быстрый-старт)
- [Синхронный клиент (RuTrackerClient)](#синхронный-клиент-rutrackerclient)
  - [Базовое использование](#базовое-использование)
  - [Поиск на одной странице](#поиск-на-одной-странице)
  - [Поиск на всех страницах](#поиск-на-всех-страницах)
  - [Скачивание торрентов](#скачивание-торрентов)
  - [Работа с формой поиска](#работа-с-формой-поиска)
  - [Использование прокси](#использование-прокси)
  - [Контекстный менеджер](#контекстный-менеджер)
- [Асинхронный клиент (AsyncRuTrackerClient)](#асинхронный-клиент-asyncrutrackerclient)
  - [Базовое использование](#базовое-использование-1)
  - [Параллельный поиск](#параллельный-поиск)
  - [Скачивание торрентов](#скачивание-торрентов-1)
  - [Работа с формой поиска](#работа-с-формой-поиска-1)
- [Логирование](#логирование)
- [Обработка ошибок](#обработка-ошибок)

---

## Быстрый старт

### Синхронный клиент

```python
from py_rutracker import RuTrackerClient

# Создание клиента
client = RuTrackerClient("your_login", "your_password")

# Поиск
results = client.search("Static-X")

# Вывод результатов
for result in results:
    print(f"{result.title} - {result.size} {result.unit}")

# Скачивание первого торрента
if results:
    file_path = client.download(results[0].topic_id, save_path="./torrents")
    print(f"Торрент сохранен: {file_path}")
```

### Асинхронный клиент

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        results = await client.search("Static-X")
        for result in results:
            print(f"{result.title} - {result.size} {result.unit}")
        
        if results:
            file_path = await client.download(
                results[0].topic_id,
                save_path="./torrents"
            )
            print(f"Торрент сохранен: {file_path}")

asyncio.run(main())
```

---

## Синхронный клиент (RuTrackerClient)

### Базовое использование

```python
from py_rutracker import RuTrackerClient

# Создание клиента с учетными данными
client = RuTrackerClient("your_login", "your_password")

# Поиск раздач по запросу
results = client.search_all_pages("Static-X")

# Вывод информации о каждой раздаче
for torrent in results:
    print(torrent)
    print("-" * 50)
```

**Пример вывода:**
```
Topic ID: 65341
Title: (Industrial, Alternative) Static-X - Start A War - 2005, APE (image + .cue), lossless
Author: SLTK
Category: Alternative & Nu-metal (lossless)
Size: 310.41 MB
Download URL: https://rutracker.org/forum/dl.php?t=65341
Added: 27-08-2006 10:53:01
Seed: 10
Leech: 0
Download Counter: 2526
--------------------------------------------------
```

### Поиск на одной странице

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Поиск на первой странице
results = client.search("Static-X", page=1)

print(f"Найдено результатов на странице 1: {len(results)}")

# Поиск на второй странице
results_page_2 = client.search("Static-X", page=2)
print(f"Найдено результатов на странице 2: {len(results_page_2)}")
```

### Поиск на всех страницах

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Поиск на всех страницах (до 10 по умолчанию)
all_results = client.search_all_pages("Static-X")
print(f"Всего найдено результатов: {len(all_results)}")

# Поиск с ограничением количества страниц
limited_results = client.search_all_pages("Static-X", max_pages=5)
print(f"Найдено результатов на 5 страницах: {len(limited_results)}")

# Получение результатов в виде словарей
results_dict = client.search_all_pages("Static-X", return_search_dict=True)
for result in results_dict:
    print(result["title"], result["size"], result["unit"])
```

### Скачивание торрентов

#### Вариант 1: Автоматическое сохранение (рекомендуется)

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")
results = client.search_all_pages("Static-X")

if results:
    topic_id = results[0].topic_id
    
    # Автоматически сохраняет файл в указанную директорию
    file_path = client.download(
        topic_id,
        save_path="./torrents",  # Путь к папке для сохранения
        filename=None  # Если None, используется topic_id.torrent
    )
    print(f"Торрент сохранен: {file_path}")
```

#### Вариант 2: Получение байтов для дополнительной обработки

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")
results = client.search_all_pages("Static-X")

if results:
    topic_id = results[0].topic_id
    
    # Получаем байты для дополнительной обработки
    bytes_data = client.get_torrent(topic_id)
    
    # Можно сохранить с кастомным именем
    with open(f"{results[0].title[:50]}.torrent", "wb") as file:
        file.write(bytes_data)
    
    # Или обработать байты перед сохранением
    # processed_data = process_torrent(bytes_data)
```

#### Скачивание по URL

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Можно использовать URL вместо topic_id
url = "https://rutracker.org/forum/dl.php?t=12345"
file_path = client.download(url, save_path="./torrents")
```

### Работа с формой поиска

#### Получение данных формы

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Получить форму поиска (будет закеширована на 24 часа)
form_data = client.get_search_form()

print(f"Найдено групп разделов: {len(form_data.forum_groups)}")
print(f"Найдено опций сортировки: {len(form_data.sort_options)}")
print(f"Найдено направлений сортировки: {len(form_data.sort_directions)}")
print(f"Найдено фильтров по времени: {len(form_data.time_filter_options)}\n")

# Просмотр групп разделов
print("Группы разделов:")
for group in form_data.forum_groups:
    print(f"\n{group.name} ({len(group.sections)} разделов)")
    for section in group.sections[:5]:  # Первые 5 разделов
        indent = "  " if section.parent_id else ""
        print(f"{indent}- [{section.id}] {section.name}")
        if section.has_subforums:
            print(f"{indent}  (есть подразделы)")

# Просмотр опций сортировки
print("\n\nОпции сортировки:")
for option in form_data.sort_options:
    selected = "✓" if option.is_selected else " "
    print(f"  [{selected}] {option.value}: {option.name}")

# Просмотр направлений сортировки
print("\n\nНаправления сортировки:")
for direction in form_data.sort_directions:
    selected = "✓" if direction.is_selected else " "
    print(f"  [{selected}] {direction.value}: {direction.name}")

# Просмотр фильтров по времени
print("\n\nФильтры по времени:")
for time_filter in form_data.time_filter_options:
    selected = "✓" if time_filter.is_selected else " "
    print(f"  [{selected}] {time_filter.value}: {time_filter.name}")

# Второй вызов - данные будут взяты из кеша
print("\n\nВторой вызов get_search_form() - данные из кеша:")
form_data_cached = client.get_search_form()
print(f"Данные получены из кеша: {form_data_cached == form_data}")

# Принудительное обновление кеша
print("\n\nПринудительное обновление кеша:")
form_data_refreshed = client.get_search_form(force_refresh=True)
print(f"Кеш обновлен, получено групп: {len(form_data_refreshed.forum_groups)}")
```

#### Поиск через форму с параметрами сортировки

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Простой поиск через форму (используются значения по умолчанию из формы)
results = client.search_with_form("Static-X")
print(f"Найдено результатов: {len(results)}")

# Поиск с сортировкой по дате (по убыванию - самые новые сначала)
results = client.search_with_form(
    "Static-X",
    sort_option=10,  # По дате добавления
    sort_direction=2  # По убыванию (2 = убывание, 1 = возрастание)
)

for result in results[:5]:  # Первые 5 результатов
    print(f"{result.title} - Добавлено: {result.added}")

# Поиск с сортировкой по размеру (по возрастанию - от меньшего к большему)
results = client.search_with_form(
    "Static-X",
    sort_option=7,   # По размеру
    sort_direction=1  # По возрастанию
)

for result in results[:5]:
    print(f"{result.title} - Размер: {result.size} {result.unit}")

# Поиск с сортировкой по количеству скачиваний (по убыванию)
results = client.search_with_form(
    "Static-X",
    sort_option=8,   # По количеству скачиваний
    sort_direction=2  # По убыванию
)

for result in results[:5]:
    print(f"{result.title} - Скачиваний: {result.download_counter}")
```

#### Поиск в конкретных форумах

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Получаем список форумов из формы
form_data = client.get_search_form()

# Находим ID музыкальных форумов (пример)
music_forums = []
for group in form_data.forum_groups:
    if "Музыка" in group.name:
        for section in group.sections:
            music_forums.append(section.id)

print(f"Найдено музыкальных форумов: {len(music_forums)}")

# Поиск только в музыкальных форумах
results = client.search_with_form(
    "Static-X",
    forum_ids=music_forums[:5],  # Первые 5 форумов
    sort_option=10,
    sort_direction=2
)

print(f"Найдено результатов в музыкальных форумах: {len(results)}")
for result in results:
    print(f"{result.category}: {result.title}")
```

#### Поиск с фильтром по времени

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Получаем доступные фильтры по времени
form_data = client.get_search_form()
print("Доступные фильтры по времени:")
for time_filter in form_data.time_filter_options:
    print(f"  {time_filter.value}: {time_filter.name}")

# Поиск за последние 7 дней
results = client.search_with_form(
    "Static-X",
    time_filter=7,  # За последние 7 дней
    sort_option=10,
    sort_direction=2
)

print(f"Найдено результатов за последние 7 дней: {len(results)}")
for result in results:
    print(f"{result.title} - Добавлено: {result.added}")

# Поиск за последние 30 дней
results = client.search_with_form(
    "Static-X",
    time_filter=30,  # За последние 30 дней
    sort_option=10,
    sort_direction=2
)

print(f"Найдено результатов за последние 30 дней: {len(results)}")
```

#### Поиск по всем страницам через форму

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Поиск по всем страницам через форму с сортировкой
# Автоматически использует POST для первой страницы и GET с search_id для остальных
all_results = client.search_all_pages_with_form(
    "Static-X",
    max_pages=10,
    sort_option=10,  # По дате
    sort_direction=2  # По убыванию
)

print(f"Найдено результатов на всех страницах: {len(all_results)}")

# Группировка по категориям
categories = {}
for result in all_results:
    if result.category not in categories:
        categories[result.category] = []
    categories[result.category].append(result)

print("\nРезультаты по категориям:")
for category, results in sorted(categories.items()):
    print(f"{category}: {len(results)} результатов")
```

#### Комбинирование параметров поиска

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Комплексный поиск: конкретные форумы + фильтр по времени + сортировка
results = client.search_with_form(
    "Static-X",
    forum_ids=[1950, 1951],  # Конкретные форумы
    time_filter=7,            # За последние 7 дней
    sort_option=10,           # По дате
    sort_direction=2          # По убыванию
)

print(f"Найдено результатов с примененными фильтрами: {len(results)}")
for result in results:
    print(f"[{result.category}] {result.title}")
    print(f"  Размер: {result.size} {result.unit}")
    print(f"  Добавлено: {result.added}")
    print(f"  Скачиваний: {result.download_counter}")
    print()
```

#### Использование значений по умолчанию из формы

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Получаем форму для просмотра значений по умолчанию
form_data = client.get_search_form()

# Используем свойства для быстрого доступа к значениям по умолчанию
if form_data.default_sort_option:
    print(f"Опция сортировки по умолчанию: {form_data.default_sort_option.value} - {form_data.default_sort_option.name}")

if form_data.default_sort_direction:
    print(f"Направление сортировки по умолчанию: {form_data.default_sort_direction.value} - {form_data.default_sort_direction.name}")

# Поиск с использованием значений по умолчанию
# Если не указать sort_option и sort_direction, они будут взяты из формы автоматически
results = client.search_with_form("Static-X")
print(f"Найдено результатов с настройками по умолчанию: {len(results)}")

# Или явно указать значения из формы
if form_data.default_sort_option and form_data.default_sort_direction:
    results = client.search_with_form(
        "Static-X",
        sort_option=form_data.default_sort_option.value,
        sort_direction=form_data.default_sort_direction.value
    )
    print(f"Найдено результатов с явно указанными значениями: {len(results)}")
```

#### Удобный поиск значений по названию

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Получаем форму
form_data = client.get_search_form()

# Поиск опции сортировки по названию (частичное совпадение, регистронезависимо)
sort_option = form_data.get_sort_option_by_name("дате")
if sort_option:
    print(f"Найдена опция сортировки: {sort_option.name} (value={sort_option.value})")
    results = client.search_with_form("Static-X", sort_option=sort_option.value)

# Поиск направления сортировки по названию
sort_direction = form_data.get_sort_direction_by_name("убыванию")
if sort_direction:
    print(f"Найдено направление: {sort_direction.name} (value={sort_direction.value})")
    results = client.search_with_form(
        "Static-X",
        sort_option=10,
        sort_direction=sort_direction.value
    )

# Поиск фильтра по времени по названию
time_filter = form_data.get_time_filter_by_name("7 дней")
if time_filter:
    print(f"Найден фильтр: {time_filter.name} (value={time_filter.value})")
    results = client.search_with_form(
        "Static-X",
        time_filter=time_filter.value
    )

# Поиск форумов по названию группы
music_forums = form_data.get_forum_ids_by_group_name("Музыка")
print(f"Найдено музыкальных форумов: {len(music_forums)}")
if music_forums:
    results = client.search_with_form(
        "Static-X",
        forum_ids=music_forums[:5]  # Первые 5 форумов
    )

# Поиск форумов по названию раздела (может найти несколько)
film_forums = form_data.get_forum_ids_by_name("Фильмы")
print(f"Найдено форумов с 'Фильмы' в названии: {len(film_forums)}")
if film_forums:
    results = client.search_with_form(
        "Static-X",
        forum_ids=film_forums
    )
```

### Использование прокси

```python
from py_rutracker import RuTrackerClient

# Настройка прокси
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'http://proxy.example.com:8080'
}

# Создание клиента с прокси
client = RuTrackerClient("your_login", "your_password", proxies=proxies)

# Использование клиента как обычно
results = client.search("Static-X")
```

### Контекстный менеджер

Использование контекстного менеджера гарантирует автоматическое закрытие сессии:

```python
from py_rutracker import RuTrackerClient

# Сессия автоматически закроется после выхода из блока
with RuTrackerClient("your_login", "your_password") as client:
    results = client.search_all_pages("Static-X")
    for torrent in results:
        print(torrent)
    
    if results:
        client.download(results[0].topic_id, save_path="./torrents")

# Сессия уже закрыта здесь
```

---

## Асинхронный клиент (AsyncRuTrackerClient)

### Базовое использование

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        results = await client.search_all_pages("rammstein")
        
        for result in results:
            print(f"{result.title} - {result.size} {result.unit}")
        
        if results:
            file_path = await client.download(
                results[0].topic_id,
                save_path="./torrents",
                filename=f"{results[0].title[:50]}.torrent"
            )
            print(f"Торрент сохранен: {file_path}")

asyncio.run(main())
```

### Параллельный поиск

Асинхронный клиент выполняет запросы к разным страницам параллельно:

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        # Запросы к страницам 1-10 выполняются параллельно
        all_results = await client.search_all_pages("Static-X", max_pages=10)
        print(f"Найдено результатов: {len(all_results)}")

asyncio.run(main())
```

### Скачивание торрентов

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        results = await client.search("Static-X")
        
        if results:
            # Вариант 1: Автоматическое сохранение
            file_path = await client.download(
                results[0].topic_id,
                save_path="./torrents",
                filename=f"{results[0].title[:50]}.torrent"
            )
            print(f"Торрент сохранен: {file_path}")
            
            # Вариант 2: Получение байтов
            # bytes_data = await client.get_torrent(results[0].topic_id)
            # with open(f"{results[0].topic_id}.torrent", "wb") as file:
            #     file.write(bytes_data)

asyncio.run(main())
```

### Работа с формой поиска

#### Получение данных формы

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        # Получить форму поиска (будет закеширована на 24 часа)
        form_data = await client.get_search_form()
        
        print(f"Найдено групп разделов: {len(form_data.forum_groups)}")
        print(f"Найдено опций сортировки: {len(form_data.sort_options)}")
        
        # Просмотр групп разделов
        for group in form_data.forum_groups[:3]:
            print(f"\n{group.name} ({len(group.sections)} разделов)")
            for section in group.sections[:3]:
                print(f"  - [{section.id}] {section.name}")
        
        # Второй вызов - данные из кеша
        form_data_cached = await client.get_search_form()
        print(f"\nДанные из кеша: {form_data_cached == form_data}")
        
        # Принудительное обновление
        form_data_refreshed = await client.get_search_form(force_refresh=True)
        print(f"Кеш обновлен")

asyncio.run(main())
```

#### Поиск через форму с параметрами сортировки

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        # Простой поиск через форму
        results = await client.search_with_form("Static-X")
        print(f"Найдено результатов: {len(results)}")
        
        # Поиск с сортировкой по дате (по убыванию)
        results = await client.search_with_form(
            "Static-X",
            sort_option=10,  # По дате
            sort_direction=2  # По убыванию
        )
        
        for result in results[:5]:
            print(f"{result.title} - Добавлено: {result.added}")
        
        # Поиск в конкретных форумах с фильтром по времени
        results = await client.search_with_form(
            "Static-X",
            forum_ids=[1950, 1951],  # Музыкальные форумы
            time_filter=7,            # За последние 7 дней
            sort_option=10,
            sort_direction=2
        )
        
        print(f"\nНайдено результатов с фильтрами: {len(results)}")

asyncio.run(main())
```

#### Поиск по всем страницам через форму

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        # Поиск по всем страницам через форму
        # Автоматически использует POST для первой страницы и GET с search_id для остальных
        all_results = await client.search_all_pages_with_form(
            "Static-X",
            max_pages=10,
            sort_option=10,
            sort_direction=2
        )
        
        print(f"Найдено результатов на всех страницах: {len(all_results)}")
        
        # Группировка по категориям
        categories = {}
        for result in all_results:
            if result.category not in categories:
                categories[result.category] = []
            categories[result.category].append(result)
        
        print("\nРезультаты по категориям:")
        for category, results in sorted(categories.items()):
            print(f"{category}: {len(results)} результатов")

asyncio.run(main())
```

#### Использование значений по умолчанию из формы (асинхронный клиент)

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        # Получаем форму для просмотра значений по умолчанию
        form_data = await client.get_search_form()
        
        # Используем свойства для быстрого доступа к значениям по умолчанию
        if form_data.default_sort_option:
            print(f"Опция сортировки по умолчанию: {form_data.default_sort_option.value} - {form_data.default_sort_option.name}")
        
        if form_data.default_sort_direction:
            print(f"Направление сортировки по умолчанию: {form_data.default_sort_direction.value} - {form_data.default_sort_direction.name}")
        
        # Поиск с использованием значений по умолчанию
        results = await client.search_with_form("Static-X")
        print(f"Найдено результатов с настройками по умолчанию: {len(results)}")

asyncio.run(main())
```

#### Удобный поиск значений по названию (асинхронный клиент)

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        # Получаем форму
        form_data = await client.get_search_form()
        
        # Поиск опции сортировки по названию
        sort_option = form_data.get_sort_option_by_name("дате")
        if sort_option:
            print(f"Найдена опция сортировки: {sort_option.name} (value={sort_option.value})")
            results = await client.search_with_form("Static-X", sort_option=sort_option.value)
        
        # Поиск форумов по названию группы
        music_forums = form_data.get_forum_ids_by_group_name("Музыка")
        print(f"Найдено музыкальных форумов: {len(music_forums)}")
        if music_forums:
            results = await client.search_with_form(
                "Static-X",
                forum_ids=music_forums[:5]  # Первые 5 форумов
            )

asyncio.run(main())
```

### Использование без контекстного менеджера

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    client = AsyncRuTrackerClient("your_login", "your_password")
    
    try:
        # Инициализация сессии
        await client.init()
        
        # Использование клиента
        results = await client.search("Static-X")
        print(f"Найдено результатов: {len(results)}")
        
    finally:
        # Закрытие сессии
        await client.close()

asyncio.run(main())
```

---

## Логирование

### Настройка уровня логирования

#### Вариант 1: Использование функции `configure_logger`

```python
import logging
from py_rutracker import RuTrackerClient, configure_logger

# Установить уровень INFO
configure_logger(level='INFO')

# Или использовать константы из модуля logging
configure_logger(level=logging.DEBUG)

# С записью в файл
configure_logger(
    level='DEBUG',
    log_to_file=True,
    log_file_path="rutracker.log"
)

client = RuTrackerClient("your_login", "your_password")
```

#### Вариант 2: Использование переменной окружения

Установите переменную окружения перед запуском:

**Linux/macOS:**
```bash
export PY_RUTRACKER_LOG_LEVEL=DEBUG
python your_script.py
```

**Windows:**
```cmd
set PY_RUTRACKER_LOG_LEVEL=DEBUG
python your_script.py
```

**Доступные уровни:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### Что логируется

- **DEBUG**: Детальная информация о всех операциях (HTTP-запросы, параметры поиска, закрытие сессий)
- **INFO**: Успешные операции (инициализация клиента, аутентификация, результаты поиска, загрузка торрентов)
- **WARNING**: Предупреждения (неожиданные статус-коды, ошибки на отдельных страницах)
- **ERROR**: Ошибки (ошибки аутентификации, парсинга, загрузки файлов)

### Пример настройки логирования

```python
from py_rutracker import RuTrackerClient, configure_logger

# Настройка логирования перед использованием клиента
configure_logger(
    level='DEBUG',
    log_to_file=True,
    log_file_path="rutracker.log",
    format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

client = RuTrackerClient("your_login", "your_password")
results = client.search("Static-X")
```

---

## Обработка ошибок

### Обработка всех типов исключений

```python
from py_rutracker import RuTrackerClient
from py_rutracker.exceptions import (
    RuTrackerAuthError,
    RuTrackerRequestError,
    RuTrackerParsingError,
    RuTrackerDownloadError
)

try:
    client = RuTrackerClient("your_login", "your_password")
    results = client.search("Static-X")
    
    if results:
        file_path = client.download(results[0].topic_id, save_path="./torrents")
        print(f"Торрент сохранен: {file_path}")
        
except RuTrackerAuthError as e:
    print(f"Ошибка аутентификации: {e}")
    # Возможно, требуется пройти капчу в браузере
    
except RuTrackerRequestError as e:
    print(f"Ошибка запроса: {e}")
    # Проблема с сетью или сервером
    
except RuTrackerParsingError as e:
    print(f"Ошибка парсинга: {e}")
    # Возможно, изменилась структура сайта
    
except RuTrackerDownloadError as e:
    print(f"Ошибка скачивания: {e}")
    # Файл не найден или недопустимый параметр
    
except Exception as e:
    print(f"Неожиданная ошибка: {e}")
```

### Обработка ошибок при поиске на всех страницах

```python
from py_rutracker import RuTrackerClient
from py_rutracker.exceptions import RuTrackerParsingError

client = RuTrackerClient("your_login", "your_password")

try:
    # Поиск на всех страницах
    # Если на какой-то странице произойдет ошибка, она будет логирована,
    # но поиск продолжится на следующих страницах
    results = client.search_all_pages("Static-X", max_pages=10)
    print(f"Найдено результатов: {len(results)}")
    
except RuTrackerParsingError as e:
    print(f"Критическая ошибка парсинга: {e}")
```

### Проверка результатов перед использованием

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")
results = client.search("Static-X")

# Всегда проверяйте наличие результатов
if results:
    first_result = results[0]
    print(f"Первый результат: {first_result.title}")
    
    # Проверка наличия topic_id перед скачиванием
    if first_result.topic_id:
        try:
            file_path = client.download(first_result.topic_id, save_path="./torrents")
            print(f"Торрент сохранен: {file_path}")
        except Exception as e:
            print(f"Не удалось скачать торрент: {e}")
else:
    print("Результаты не найдены")
```

---

## Дополнительные примеры

### Фильтрация результатов по размеру

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")
results = client.search_all_pages("Static-X")

# Фильтрация результатов больше 1 GB
large_torrents = [
    r for r in results 
    if r.unit == "GB" and r.size >= 1.0
]

print(f"Найдено торрентов больше 1 GB: {len(large_torrents)}")
for torrent in large_torrents:
    print(f"{torrent.title} - {torrent.size} {torrent.unit}")
```

### Поиск с лучшим соотношением сидов/личеров

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")
results = client.search("Static-X")

# Сортировка по количеству сидов
sorted_results = sorted(
    results,
    key=lambda x: x.seedmed,
    reverse=True
)

print("Топ-5 результатов по количеству сидов:")
for i, result in enumerate(sorted_results[:5], 1):
    print(f"{i}. {result.title}")
    print(f"   Сиды: {result.seedmed}, Личеры: {result.leechmed}")
```

### Массовое скачивание торрентов

```python
from py_rutracker import RuTrackerClient
from py_rutracker.exceptions import RuTrackerDownloadError

client = RuTrackerClient("your_login", "your_password")
results = client.search_all_pages("Static-X")

# Скачивание первых 10 торрентов
downloaded = 0
failed = 0

for i, result in enumerate(results[:10], 1):
    try:
        file_path = client.download(
            result.topic_id,
            save_path="./torrents",
            filename=f"{i}_{result.topic_id}.torrent"
        )
        print(f"[{i}/10] Скачан: {result.title[:50]}")
        downloaded += 1
    except RuTrackerDownloadError as e:
        print(f"[{i}/10] Ошибка: {result.title[:50]} - {e}")
        failed += 1

print(f"\nСкачано: {downloaded}, Ошибок: {failed}")
```

### Асинхронное массовое скачивание

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient
from py_rutracker.exceptions import RuTrackerDownloadError

async def download_torrent(client, result, index):
    try:
        file_path = await client.download(
            result.topic_id,
            save_path="./torrents",
            filename=f"{index}_{result.topic_id}.torrent"
        )
        print(f"[{index}] Скачан: {result.title[:50]}")
        return True
    except RuTrackerDownloadError as e:
        print(f"[{index}] Ошибка: {result.title[:50]} - {e}")
        return False

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        results = await client.search_all_pages("Static-X")
        
        # Параллельное скачивание первых 10 торрентов
        tasks = [
            download_torrent(client, result, i)
            for i, result in enumerate(results[:10], 1)
        ]
        
        results_download = await asyncio.gather(*tasks)
        downloaded = sum(results_download)
        
        print(f"\nСкачано: {downloaded} из {len(tasks)}")

asyncio.run(main())
```

---

## Готовые примеры

В папке `examples/` находятся готовые примеры использования библиотеки:

- **`basic_usage.py`** — базовое использование синхронного клиента
- **`async_usage.py`** — пример использования асинхронного клиента
- **`get_search_form.py`** — работа с формой поиска (синхронный клиент)
- **`get_search_form_async.py`** — работа с формой поиска (асинхронный клиент)
- **`logging_example.py`** — примеры настройки логирования

Вы можете запустить любой пример:

```bash
python examples/basic_usage.py
python examples/async_usage.py
python examples/get_search_form.py
python examples/get_search_form_async.py
python examples/logging_example.py
```

**Примечание:** Перед запуском примеров установите переменные окружения:
```bash
export LOGIN="your_login"
export PASSWORD="your_password"
export PROXY="http://proxy:8080"  # Опционально
```

