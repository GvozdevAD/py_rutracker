# Py_RuTracker

Py_RuTracker — это библиотека для работы с RuTracker, популярным российским торрент-трекером. Она предоставляет удобный интерфейс для поиска и получения информации о раздачах на RuTracker.

## Содержание

- [Установка](#установка)
- [Пример использования AsyncRuTrackerClient](#пример-использования-asyncrutrackerclient)
- [Пример использования RuTrackerClient](#пример-использования-rutrackerclient)
  - [Обычное использование](#обычное-использование)
  - [Использование через контекстный менеджер](#использование-через-контекстный-менеджер)
  - [Пример вывода](#пример-вывода)
  - [Скачать .torrent файл](#скачать-torrent-файл)
- [Логирование](#логирование)
- [Технологии](#технологии)
- [Примеры](#примеры)
- [Документация](#документация)
  - [Методы класса `RuTrackerClient`](#методы-класса-rutrackerclient)
    - `search`
    - `search_all_pages`
    - `download`
- [Внесение вклада](#внесение-вклада)
- [Примечания](#примечания)


## Установка 

Вы можете установить библиотеку двумя способами: с помощью `pip` или через `git clone`.

### Установка с PyPI

Для установки библиотеки используйте `pip`:

```sh
pip install py-rutracker-client
```

### Установка через `git clone`

1. Клонируйте репозиторий:
    ```sh
    git clone https://github.com/GvozdevAD/py_rutracker
    cd py_rutracker
    ```
2. Создайте виртуальное окружение с помощью `venv`:
    ```sh
    python -m venv env
    ```
3. Активируйте виртуальное окружение:
    * На Windows:
        ```sh
        env\Scripts\activate
        ```
    * На macOS и Linux:
        ```sh
        source env/bin/activate
        ```
4. Установите зависимости из `requirements.txt`:
    ```sh
    pip install -r requirements.txt
    ```

## Пример использования AsyncRuTrackerClient

```python

import asyncio

from py_rutracker import AsyncRuTrackerClient

login = "your_login"
password = "your_password"
proxies = 'http://<PROXY_IP_ADDRESS>:<PROXY_PORT>'

async def main():
     async with AsyncRuTrackerClient(login, password, proxies) as client:
          results = await client.search_all_pages("rammstein")
          if results:
              # Автоматическое сохранение файла
              file_path = await client.download(
                  results[0].topic_id,
                  save_path="./torrents"
              )
              print(f"Торрент сохранен: {file_path}")

asyncio.run(main())
```

## Пример использования RuTrackerClient

### Обычное использование

Если вам нужно использовать прокси, вы можете создать словарь с прокси-серверами:
```python
from py_rutracker import RuTrackerClient

proxies = {
    'http': 'http://<PROXY_IP_ADDRESS>:<PROXY_PORT>',
    'https': 'http://<PROXY_IP_ADDRESS>:<PROXY_PORT>'
}

# Создание клиента с вашими учетными данными и прокси (если необходимо)
client = RuTrackerClient("your_login", "your_password", proxies)

# Поиск раздач по запросу
results = client.search_all_pages("Static-X")

# Вывод информации о каждой раздаче
for torrent in results:
    print(torrent)
```
### Использование через контекстный менеджер

Вы можете использовать RuTrackerClient через контекстный менеджер with, чтобы автоматически закрыть соединение после завершения работы:

```python
from py_rutracker import RuTrackerClient

with RuTrackerClient(login="your_login", password="your_password") as client:
    results = client.search_all_pages("Static-X")
    for torrent in results:
        print(torrent)

```

### Пример вывода
```sh
...
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
...
```

### Скачать .torrent файл

#### Вариант 1: Автоматическое сохранение (рекомендуется)
```python
from py_rutracker import RuTrackerClient

with RuTrackerClient("your_login", "your_password") as client:
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

with RuTrackerClient("your_login", "your_password") as client:
     results = client.search_all_pages("Static-X")
     if results:
         topic_id = results[0].topic_id
         # Получаем байты для дополнительной обработки
         bytes_data = client.get_torrent(topic_id)
         with open(f"{topic_id}.torrent", "wb") as file:
              file.write(bytes_data)
```

## Логирование

Библиотека использует централизованное логирование. По умолчанию логируются только сообщения уровня **WARNING** и выше, чтобы не засорять вывод. Для отладки можно включить более подробное логирование.

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

```bash
export PY_RUTRACKER_LOG_LEVEL=DEBUG
```

Или в Windows:

```cmd
set PY_RUTRACKER_LOG_LEVEL=DEBUG
```

Доступные уровни: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### Что логируется

- **DEBUG**: Детальная информация о всех операциях (HTTP-запросы, параметры поиска, закрытие сессий)
- **INFO**: Успешные операции (инициализация клиента, аутентификация, результаты поиска, загрузка торрентов)
- **WARNING**: Предупреждения (неожиданные статус-коды, ошибки на отдельных страницах)
- **ERROR**: Ошибки (ошибки аутентификации, парсинга, загрузки файлов)

## Технологии

Библиотека использует современные технологии и лучшие практики:

- **Pydantic** — для валидации данных и моделей. Все модели данных (`SearchResult`) используют Pydantic для автоматической валидации типов и значений.
- **aiohttp** — для асинхронных HTTP-запросов
- **requests** — для синхронных HTTP-запросов
- **BeautifulSoup4** — для парсинга HTML
- **Централизованное логирование** — для удобной отладки и мониторинга

### Преимущества использования Pydantic

- Автоматическая валидация типов данных
- Преобразование типов (например, строки в числа)
- Валидация значений (проверка диапазонов, форматов)
- Удобная сериализация в JSON
- Подробные сообщения об ошибках при валидации

## Примеры

В папке `examples/` находятся готовые примеры использования библиотеки:

- **`basic_usage.py`** — базовое использование синхронного клиента
- **`async_usage.py`** — пример использования асинхронного клиента
- **`logging_example.py`** — примеры настройки логирования

Вы можете запустить любой пример:

```bash
python examples/basic_usage.py
python examples/async_usage.py
python examples/logging_example.py
```

## Документация

### Методы класса RuTrackerClient

* `search(title: str, page: int = 1, return_search_dict: bool = False) -> list[SearchResult | dict]`  
    Выполняет поиск по заданному заголовку и возвращает результаты.  
    `title`: Заголовок для поиска.  
    `page`: Номер страницы для поиска (по умолчанию 1).  
    `return_search_dict`: Флаг, указывающий, следует ли возвращать результаты в виде словарей (если True) или объектов SearchResult (если False).  
* `search_all_pages(title: str, return_search_dict: bool = False) -> list[SearchResult | dict]`  
    Выполняет поиск по заданному заголовку на всех страницах (до 10 страниц).  
    `title`: Заголовок для поиска.  
    `return_search_dict`: Флаг, указывающий, следует ли возвращать результаты в виде словарей (если True) или объектов SearchResult (если False).  
* `get_torrent(topic_id_or_url: int | str) -> bytes`  
    Получает содержимое файла торрента по указанному идентификатору или URL.  
    `topic_id_or_url`: Идентификатор (топика) или URL для получения файла торрента.  
    Возвращает: Содержимое файла торрента в виде байтов.  
* `download(topic_id_or_url: int | str, save_path: str = None, filename: str = None) -> str`  
    Скачивает файл торрента и сохраняет его на диск.  
    `topic_id_or_url`: Идентификатор (топика) или URL для получения файла торрента.  
    `save_path`: Путь к директории для сохранения файла (если None, используется текущая директория).  
    `filename`: Имя файла (если None, используется topic_id.torrent).  
    Возвращает: Полный путь к сохраненному файлу.  

## Внесение вклада

Вклад в развитие проекта приветствуется! Если вы хотите помочь проекту:

1. **Создайте отдельную ветку** от `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Внесите изменения** и убедитесь, что код соответствует стилю проекта

3. **Создайте Merge Request (MR)** в ветку `develop`:
   - Убедитесь, что ваши изменения не ломают существующий функционал
   - Добавьте описание изменений в MR
   - Укажите связанные issues (если есть)

4. **Дождитесь ревью** — я рассмотрю ваш MR и при необходимости предложу улучшения

### Структура проекта

```
py_rutracker/
├── clients/          # Клиенты (sync, async)
├── core/             # Ядро библиотеки (базовый класс, константы)
├── models/           # Модели данных (Pydantic)
├── parsers/          # Парсеры HTML
├── utils/            # Утилиты (валидация, хелперы)
├── logger.py         # Централизованное логирование
├── exceptions.py     # Исключения
└── enums.py          # Перечисления
```

## Примечания

* Замените "your_login" и "your_password" на ваши действительные учетные данные RuTracker.
* Укажите прокси в словаре, если ваш запрос требует использования прокси. Если прокси не требуется, вы можете не указывать этот параметр.
* Библиотека использует неофициальный API RuTracker и может не работать в случае изменений на сайте.