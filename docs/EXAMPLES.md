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

