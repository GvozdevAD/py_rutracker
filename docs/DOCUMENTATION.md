# Документация API

Полная документация по использованию библиотеки Py_RuTracker.

## Содержание

- [RuTrackerClient (Синхронный клиент)](#rutrackerclient-синхронный-клиент)
  - [Инициализация](#инициализация)
  - [Поиск](#поиск)
    - [search() - простой поиск](#search---простой-поиск)
    - [search_all_pages() - поиск на всех страницах](#search_all_pages---поиск-на-всех-страницах)
    - [search_with_form() - поиск через форму](#search_with_form---поиск-через-форму)
    - [search_all_pages_with_form() - поиск по всем страницам через форму](#search_all_pages_with_form---поиск-по-всем-страницам-через-форму)
  - [Работа с торрентами](#работа-с-торрентами)
  - [Форма поиска](#форма-поиска)
  - [Аутентификация](#аутентификация)
  - [Контекстный менеджер](#контекстный-менеджер)
- [AsyncRuTrackerClient (Асинхронный клиент)](#asyncrutrackerclient-асинхронный-клиент)
  - [Инициализация](#инициализация-1)
  - [Поиск](#поиск-1)
  - [Работа с торрентами](#работа-с-торрентами-1)
  - [Форма поиска](#форма-поиска-1)
  - [Аутентификация](#аутентификация-1)
  - [Управление сессией](#управление-сессией)
  - [Контекстный менеджер](#контекстный-менеджер-1)
- [Модели данных](#модели-данных)
  - [SearchResult](#searchresult)
  - [SearchFormData](#searchformdata)
- [Исключения](#исключения)

---

## RuTrackerClient (Синхронный клиент)

### Инициализация

#### `__init__(login: str, password: str, proxies: Optional[dict] = None)`

Инициализирует синхронный клиент RuTracker и выполняет аутентификацию.

**Параметры:**
- `login` (str): Логин для аутентификации.
- `password` (str): Пароль для аутентификации.
- `proxies` (Optional[dict]): Опциональный словарь с прокси-серверами для HTTP и HTTPS.

**Пример:**
```python
from py_rutracker import RuTrackerClient

# Без прокси
client = RuTrackerClient("your_login", "your_password")

# С прокси
proxies = {
    'http': 'http://proxy:8080',
    'https': 'http://proxy:8080'
}
client = RuTrackerClient("your_login", "your_password", proxies)
```

**Исключения:**
- `RuTrackerAuthError`: Если аутентификация не удалась или обнаружена капча.

---

### Поиск

Библиотека предоставляет два способа поиска:

1. **Простой поиск** (`search()`, `search_all_pages()`) - использует GET запросы, работает как раньше, поддерживает только базовые параметры (`title`, `page`).
2. **Поиск через форму** (`search_with_form()`, `search_all_pages_with_form()`) - использует POST запрос для первой страницы и GET с `search_id` для последующих, поддерживает расширенные параметры (сортировка, фильтры по форумам и времени).

**Когда использовать поиск через форму:**
- Нужна сортировка результатов (по дате, размеру, количеству скачиваний и т.д.)
- Нужна фильтрация по конкретным форумам
- Нужна фильтрация по времени (за последние 7 дней, месяц и т.д.)
- Нужен более точный контроль над параметрами поиска

**Когда использовать простой поиск:**
- Нужен быстрый поиск без дополнительных параметров
- Совместимость со старым кодом
- Простые задачи поиска

#### `search()` - простой поиск

#### `search(title: str, page: int = 1, return_search_dict: bool = False) -> list[SearchResult | dict]`

Выполняет поиск по заданному заголовку и возвращает результаты. Использует GET запросы.

**Параметры:**
- `title` (str): Заголовок для поиска.
- `page` (int): Номер страницы для поиска (по умолчанию 1).
- `return_search_dict` (bool): Флаг, указывающий, следует ли возвращать результаты в виде словарей (если `True`) или объектов `SearchResult` (если `False`).

**Возвращает:**
- `list[SearchResult | dict]`: Список результатов поиска.

**Исключения:**
- `RuTrackerRequestError`: Если происходит ошибка при выполнении запроса.
- `RuTrackerParsingError`: Если происходит ошибка при парсинге результатов поиска.

**Пример:**
```python
# Получить результаты как объекты SearchResult
results = client.search("Static-X", page=1)

# Получить результаты как словари
results_dict = client.search("Static-X", page=1, return_search_dict=True)

for result in results:
    print(f"{result.title} - {result.size} {result.unit}")
```

#### `search_all_pages()` - поиск на всех страницах

#### `search_all_pages(title: str, return_search_dict: bool = False, max_pages: Optional[int] = None) -> list[SearchResult | dict]`

Выполняет поиск по заданному заголовку на всех страницах. Использует GET запросы.

**Параметры:**
- `title` (str): Заголовок для поиска.
- `return_search_dict` (bool): Флаг, указывающий, следует ли возвращать результаты в виде словарей (если `True`) или объектов `SearchResult` (если `False`).
- `max_pages` (Optional[int]): Максимальное количество страниц для поиска (по умолчанию 10). Если `None`, используется значение из констант.

**Возвращает:**
- `list[SearchResult | dict]`: Список всех результатов поиска со всех страниц.

**Исключения:**
- `RuTrackerParsingError`: Если происходит ошибка при парсинге результатов поиска.

**Пример:**
```python
# Поиск на всех страницах (до 10 страниц по умолчанию)
all_results = client.search_all_pages("Static-X")

# Поиск с ограничением количества страниц
limited_results = client.search_all_pages("Static-X", max_pages=5)

print(f"Найдено результатов: {len(all_results)}")
```

#### `search_with_form()` - поиск через форму

#### `search_with_form(title: str, page: int = 1, return_search_dict: bool = False, forum_ids: Optional[List[int]] = None, sort_option: Optional[int] = None, sort_direction: Optional[int] = None, time_filter: Optional[int] = None) -> list[SearchResult | dict]`

Выполняет поиск через форму с параметрами сортировки и фильтрации. Использует POST запрос для первой страницы и GET запрос с `search_id` для последующих страниц.

**Параметры:**
- `title` (str): Заголовок для поиска.
- `page` (int): Номер страницы для поиска (по умолчанию 1).
- `return_search_dict` (bool): Флаг, указывающий, следует ли возвращать результаты в виде словарей (если `True`) или объектов `SearchResult` (если `False`).
- `forum_ids` (Optional[List[int]]): Список ID форумов (по умолчанию `[-1]` - все имеющиеся).
- `sort_option` (Optional[int]): Опция сортировки (если не указана, используется из формы).
- `sort_direction` (Optional[int]): Направление сортировки (1 - возрастание, 2 - убывание, если не указано, используется из формы).
- `time_filter` (Optional[int]): Фильтр по времени (опционально).

**Возвращает:**
- `list[SearchResult | dict]`: Список результатов поиска.

**Исключения:**
- `RuTrackerValidationError`: Если параметры не проходят валидацию.
- `RuTrackerRequestError`: Если происходит ошибка при выполнении запроса.
- `RuTrackerParsingError`: Если происходит ошибка при парсинге результатов поиска.

**Пример:**
```python
# Простой поиск через форму (используются значения по умолчанию из формы)
results = client.search_with_form("Static-X")

# Поиск с сортировкой по дате (по убыванию)
results = client.search_with_form(
    "Static-X",
    sort_option=10,  # По дате
    sort_direction=2  # По убыванию
)

# Поиск в конкретных форумах с фильтром по времени
results = client.search_with_form(
    "Static-X",
    forum_ids=[1950, 1951],  # Музыкальные форумы
    time_filter=7  # За последние 7 дней
)

for result in results:
    print(f"{result.title} - {result.size} {result.unit}")
```

**Примечание:** Метод автоматически извлекает `search_id` из ответа первого POST запроса и использует его для пагинации. `search_id` кешируется для оптимизации повторных запросов с теми же параметрами.

#### `search_all_pages_with_form()` - поиск по всем страницам через форму

#### `search_all_pages_with_form(title: str, return_search_dict: bool = False, max_pages: Optional[int] = None, forum_ids: Optional[List[int]] = None, sort_option: Optional[int] = None, sort_direction: Optional[int] = None, time_filter: Optional[int] = None) -> list[SearchResult | dict]`

Выполняет поиск через форму по заданному заголовку на всех страницах. Автоматически использует POST для первой страницы и GET с `search_id` для остальных.

**Параметры:**
- `title` (str): Заголовок для поиска.
- `return_search_dict` (bool): Флаг, указывающий, следует ли возвращать результаты в виде словарей (если `True`) или объектов `SearchResult` (если `False`).
- `max_pages` (Optional[int]): Максимальное количество страниц для поиска (по умолчанию 10). Если `None`, используется значение из констант.
- `forum_ids` (Optional[List[int]]): Список ID форумов (по умолчанию `[-1]` - все имеющиеся).
- `sort_option` (Optional[int]): Опция сортировки (если не указана, используется из формы).
- `sort_direction` (Optional[int]): Направление сортировки (1 - возрастание, 2 - убывание, если не указано, используется из формы).
- `time_filter` (Optional[int]): Фильтр по времени (опционально).

**Возвращает:**
- `list[SearchResult | dict]`: Список всех результатов поиска со всех страниц.

**Исключения:**
- `RuTrackerParsingError`: Если происходит ошибка при парсинге результатов поиска.

**Пример:**
```python
# Поиск по всем страницам через форму с сортировкой
all_results = client.search_all_pages_with_form(
    "Static-X",
    max_pages=10,
    sort_option=10,
    sort_direction=2
)

print(f"Найдено результатов: {len(all_results)}")
```

---

### Работа с торрентами

#### `get_torrent(topic_id_or_url: int | str) -> bytes`

Получает содержимое файла торрента по указанному идентификатору или URL.

**Параметры:**
- `topic_id_or_url` (int | str): Идентификатор топика (int) или URL для получения файла торрента (str).

**Возвращает:**
- `bytes`: Содержимое файла торрента в виде байтов.

**Исключения:**
- `RuTrackerRequestError`: Если запрос на получение файла торрента завершился ошибкой.
- `RuTrackerDownloadError`: Если передан недопустимый параметр или файл не найден.

**Пример:**
```python
# По ID
torrent_bytes = client.get_torrent(12345)

# По URL
torrent_bytes = client.get_torrent("https://rutracker.org/forum/dl.php?t=12345")

# Сохранение вручную
with open("torrent.torrent", "wb") as f:
    f.write(torrent_bytes)
```

#### `download(topic_id_or_url: int | str, save_path: Optional[str] = None, filename: Optional[str] = None) -> str`

Скачивает файл торрента и сохраняет его на диск.

**Параметры:**
- `topic_id_or_url` (int | str): Идентификатор топика (int) или URL для получения файла торрента (str).
- `save_path` (Optional[str]): Путь к директории для сохранения файла. Если `None`, используется текущая директория.
- `filename` (Optional[str]): Имя файла. Если `None`, используется `{topic_id}.torrent`.

**Возвращает:**
- `str`: Полный путь к сохраненному файлу.

**Исключения:**
- `RuTrackerRequestError`: Если запрос на получение файла торрента завершился ошибкой.
- `RuTrackerDownloadError`: Если передан недопустимый параметр или файл не найден.

**Пример:**
```python
# Автоматическое сохранение с именем по умолчанию
file_path = client.download(12345, save_path="./torrents")
print(f"Торрент сохранен: {file_path}")

# С указанием имени файла
file_path = client.download(12345, save_path="./torrents", filename="my_torrent")
```

---

### Форма поиска

#### `get_search_form(force_refresh: bool = False) -> SearchFormData`

Получает данные формы поиска RuTracker (разделы форума, опции сортировки, фильтры по времени).  
Данные кешируются на 24 часа для уменьшения количества запросов к серверу.

**Параметры:**
- `force_refresh` (bool): Принудительно обновить кеш, игнорируя время жизни (по умолчанию `False`).

**Возвращает:**
- `SearchFormData`: Объект с данными формы поиска, содержащий:
  - `forum_groups`: Список групп разделов форума (`ForumGroup`)
  - `sort_options`: Список опций сортировки (`SortOption`)
  - `sort_directions`: Список направлений сортировки (`SortDirection`)
  - `time_filter_options`: Список опций фильтра по времени (`TimeFilterOption`)
  - `forum_field_name`: Имя поля формы для разделов форума

**Исключения:**
- `RuTrackerRequestError`: Если запрос на получение формы завершился ошибкой.
- `RuTrackerParsingError`: Если произошла ошибка при парсинге формы.

**Пример:**
```python
# Получить форму поиска (из кеша, если доступно)
form_data = client.get_search_form()

# Просмотр групп разделов
for group in form_data.forum_groups:
    print(f"{group.name}: {len(group.sections)} разделов")
    for section in group.sections:
        print(f"  - {section.name} (ID: {section.id})")

# Просмотр опций сортировки
for option in form_data.sort_options:
    print(f"{option.value}: {option.name}")

# Принудительное обновление кеша
form_data = client.get_search_form(force_refresh=True)
```

#### Вспомогательные методы SearchFormData

Класс `SearchFormData` предоставляет удобные методы для поиска значений по названию без необходимости проходить по спискам вручную:

**Методы поиска:**

- `get_sort_option_by_name(name: str) -> Optional[SortOption]` - Находит опцию сортировки по названию (частичное совпадение, регистронезависимо).
- `get_sort_option_by_value(value: int) -> Optional[SortOption]` - Находит опцию сортировки по значению.
- `get_sort_direction_by_name(name: str) -> Optional[SortDirection]` - Находит направление сортировки по названию (частичное совпадение, регистронезависимо).
- `get_time_filter_by_name(name: str) -> Optional[TimeFilterOption]` - Находит фильтр по времени по названию (частичное совпадение, регистронезависимо).
- `get_time_filter_by_value(value: int) -> Optional[TimeFilterOption]` - Находит фильтр по времени по значению.
- `get_forum_ids_by_name(name: str) -> List[int]` - Находит ID форумов по названию раздела (частичное совпадение, регистронезависимо). Может вернуть несколько ID.
- `get_forum_ids_by_group_name(group_name: str) -> List[int]` - Находит ID всех форумов в группе по названию группы (частичное совпадение, регистронезависимо).

**Свойства для значений по умолчанию:**

- `default_sort_option: Optional[SortOption]` - Возвращает выбранную опцию сортировки по умолчанию.
- `default_sort_direction: Optional[SortDirection]` - Возвращает выбранное направление сортировки по умолчанию.
- `default_time_filter: Optional[TimeFilterOption]` - Возвращает выбранный фильтр по времени по умолчанию.

**Пример использования:**
```python
form_data = client.get_search_form()

# Поиск опции сортировки по названию
sort_option = form_data.get_sort_option_by_name("дате")
if sort_option:
    results = client.search_with_form("Static-X", sort_option=sort_option.value)

# Поиск форумов по названию группы
music_forums = form_data.get_forum_ids_by_group_name("Музыка")
if music_forums:
    results = client.search_with_form("Static-X", forum_ids=music_forums)

# Использование значений по умолчанию
if form_data.default_sort_option:
    print(f"Сортировка по умолчанию: {form_data.default_sort_option.name}")
```

---

### Аутентификация

#### `auth(login: str, password: str) -> None`

Аутентифицирует пользователя на сайте RuTracker. Обычно вызывается автоматически при инициализации клиента.

**Параметры:**
- `login` (str): Логин для аутентификации.
- `password` (str): Пароль для аутентификации.

**Исключения:**
- `RuTrackerAuthError`: Если статус-код ответа не 200, аутентификация не удалась, или обнаружена капча.

**Пример:**
```python
# Обычно не требуется вызывать вручную
client.auth("your_login", "your_password")
```

---

### Контекстный менеджер

Класс `RuTrackerClient` поддерживает использование в качестве контекстного менеджера для автоматического закрытия сессии:

```python
with RuTrackerClient("login", "password") as client:
    results = client.search("query")
    # Сессия автоматически закроется после выхода из блока
```

---

## AsyncRuTrackerClient (Асинхронный клиент)

### Инициализация

#### `__init__(login: str, password: str, proxy: Optional[str] = None, user_agent: Optional[str] = None)`

Инициализирует асинхронный клиент RuTracker.

**Параметры:**
- `login` (str): Логин для аутентификации.
- `password` (str): Пароль для аутентификации.
- `proxy` (Optional[str]): Опциональный URL прокси-сервера (например, `'http://proxy:8080'`).
- `user_agent` (Optional[str]): Опциональный User-Agent для HTTP-запросов.

**Пример:**
```python
from py_rutracker import AsyncRuTrackerClient

client = AsyncRuTrackerClient("your_login", "your_password", proxy="http://proxy:8080")
```

#### `async init() -> aiohttp.ClientSession`

Инициализирует асинхронную сессию и выполняет аутентификацию.

**Возвращает:**
- `aiohttp.ClientSession`: Объект сессии aiohttp.

**Примечание:** Этот метод должен быть вызван перед использованием клиента, если не используется контекстный менеджер.

**Пример:**
```python
client = AsyncRuTrackerClient("login", "password")
await client.init()
# Теперь можно использовать клиент
results = await client.search("query")
```

---

### Поиск

#### `search()` - простой поиск

#### `async search(title: str, page: int = 1, return_search_dict: bool = False) -> list[SearchResult | dict]`

Асинхронно выполняет поиск по заданному заголовку и возвращает результаты. Использует GET запросы.

**Параметры:**
- `title` (str): Заголовок для поиска.
- `page` (int): Номер страницы для поиска (по умолчанию 1).
- `return_search_dict` (bool): Флаг, указывающий, следует ли возвращать результаты в виде словарей (если `True`) или объектов `SearchResult` (если `False`).

**Возвращает:**
- `list[SearchResult | dict]`: Список результатов поиска.

**Исключения:**
- `RuTrackerRequestError`: Если происходит ошибка при выполнении запроса.
- `RuTrackerParsingError`: Если происходит ошибка при парсинге результатов поиска.

**Пример:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    results = await client.search("Static-X", page=1)
    for result in results:
        print(f"{result.title} - {result.size} {result.unit}")
```

#### `search_all_pages()` - поиск на всех страницах

#### `async search_all_pages(title: str, return_search_dict: bool = False, max_pages: Optional[int] = None) -> list[SearchResult | dict]`

Асинхронно выполняет поиск по заданному заголовку на всех страницах. Запросы к разным страницам выполняются параллельно. Использует GET запросы.

**Параметры:**
- `title` (str): Заголовок для поиска.
- `return_search_dict` (bool): Флаг, указывающий, следует ли возвращать результаты в виде словарей (если `True`) или объектов `SearchResult` (если `False`).
- `max_pages` (Optional[int]): Максимальное количество страниц для поиска (по умолчанию 10). Если `None`, используется значение из констант.

**Возвращает:**
- `list[SearchResult | dict]`: Список всех результатов поиска со всех страниц.

**Исключения:**
- `RuTrackerParsingError`: Если происходит ошибка при парсинге результатов поиска.

**Пример:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    # Параллельный поиск на всех страницах
    all_results = await client.search_all_pages("Static-X", max_pages=5)
    print(f"Найдено результатов: {len(all_results)}")
```

#### `search_with_form()` - поиск через форму

#### `async search_with_form(title: str, page: int = 1, return_search_dict: bool = False, forum_ids: Optional[List[int]] = None, sort_option: Optional[int] = None, sort_direction: Optional[int] = None, time_filter: Optional[int] = None) -> list[SearchResult | dict]`

Асинхронно выполняет поиск через форму с параметрами сортировки и фильтрации. Использует POST запрос для первой страницы и GET запрос с `search_id` для последующих страниц.

**Параметры:**
- `title` (str): Заголовок для поиска.
- `page` (int): Номер страницы для поиска (по умолчанию 1).
- `return_search_dict` (bool): Флаг, указывающий, следует ли возвращать результаты в виде словарей (если `True`) или объектов `SearchResult` (если `False`).
- `forum_ids` (Optional[List[int]]): Список ID форумов (по умолчанию `[-1]` - все имеющиеся).
- `sort_option` (Optional[int]): Опция сортировки (если не указана, используется из формы).
- `sort_direction` (Optional[int]): Направление сортировки (1 - возрастание, 2 - убывание, если не указано, используется из формы).
- `time_filter` (Optional[int]): Фильтр по времени (опционально).

**Возвращает:**
- `list[SearchResult | dict]`: Список результатов поиска.

**Исключения:**
- `RuTrackerValidationError`: Если параметры не проходят валидацию.
- `RuTrackerRequestError`: Если происходит ошибка при выполнении запроса.
- `RuTrackerParsingError`: Если происходит ошибка при парсинге результатов поиска.

**Пример:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    # Поиск с сортировкой по дате (по убыванию)
    results = await client.search_with_form(
        "Static-X",
        sort_option=10,
        sort_direction=2
    )
    
    for result in results:
        print(f"{result.title} - {result.size} {result.unit}")
```

#### `search_all_pages_with_form()` - поиск по всем страницам через форму

#### `async search_all_pages_with_form(title: str, return_search_dict: bool = False, max_pages: Optional[int] = None, forum_ids: Optional[List[int]] = None, sort_option: Optional[int] = None, sort_direction: Optional[int] = None, time_filter: Optional[int] = None) -> list[SearchResult | dict]`

Асинхронно выполняет поиск через форму по заданному заголовку на всех страницах. Автоматически использует POST для первой страницы и GET с `search_id` для остальных.

**Параметры:**
- `title` (str): Заголовок для поиска.
- `return_search_dict` (bool): Флаг, указывающий, следует ли возвращать результаты в виде словарей (если `True`) или объектов `SearchResult` (если `False`).
- `max_pages` (Optional[int]): Максимальное количество страниц для поиска (по умолчанию 10). Если `None`, используется значение из констант.
- `forum_ids` (Optional[List[int]]): Список ID форумов (по умолчанию `[-1]` - все имеющиеся).
- `sort_option` (Optional[int]): Опция сортировки (если не указана, используется из формы).
- `sort_direction` (Optional[int]): Направление сортировки (1 - возрастание, 2 - убывание, если не указано, используется из формы).
- `time_filter` (Optional[int]): Фильтр по времени (опционально).

**Возвращает:**
- `list[SearchResult | dict]`: Список всех результатов поиска со всех страниц.

**Исключения:**
- `RuTrackerParsingError`: Если происходит ошибка при парсинге результатов поиска.

**Пример:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    all_results = await client.search_all_pages_with_form(
        "Static-X",
        max_pages=10,
        sort_option=10,
        sort_direction=2
    )
    print(f"Найдено результатов: {len(all_results)}")
```

---

### Работа с торрентами

#### `async get_torrent(topic_id_or_url: int | str) -> bytes`

Асинхронно получает содержимое файла торрента по указанному идентификатору или URL.

**Параметры:**
- `topic_id_or_url` (int | str): Идентификатор топика (int) или URL для получения файла торрента (str).

**Возвращает:**
- `bytes`: Содержимое файла торрента в виде байтов.

**Исключения:**
- `RuTrackerRequestError`: Если запрос на получение файла торрента завершился ошибкой.
- `RuTrackerDownloadError`: Если передан недопустимый параметр или файл не найден.

**Пример:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    torrent_bytes = await client.get_torrent(12345)
    with open("torrent.torrent", "wb") as f:
        f.write(torrent_bytes)
```

#### `async download(topic_id_or_url: int | str, save_path: Optional[str] = None, filename: Optional[str] = None) -> str`

Асинхронно скачивает файл торрента и сохраняет его на диск.

**Параметры:**
- `topic_id_or_url` (int | str): Идентификатор топика (int) или URL для получения файла торрента (str).
- `save_path` (Optional[str]): Путь к директории для сохранения файла. Если `None`, используется текущая директория.
- `filename` (Optional[str]): Имя файла. Если `None`, используется `{topic_id}.torrent`.

**Возвращает:**
- `str`: Полный путь к сохраненному файлу.

**Исключения:**
- `RuTrackerRequestError`: Если запрос на получение файла торрента завершился ошибкой.
- `RuTrackerDownloadError`: Если передан недопустимый параметр или файл не найден.

**Пример:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    results = await client.search("Static-X")
    if results:
        file_path = await client.download(
            results[0].topic_id,
            save_path="./torrents",
            filename=f"{results[0].title[:50]}.torrent"
        )
        print(f"Торрент сохранен: {file_path}")
```

---

### Форма поиска

#### `async get_search_form(force_refresh: bool = False) -> SearchFormData`

Асинхронно получает данные формы поиска RuTracker (разделы форума, опции сортировки, фильтры по времени).  
Данные кешируются на 24 часа для уменьшения количества запросов к серверу.

**Параметры:**
- `force_refresh` (bool): Принудительно обновить кеш, игнорируя время жизни (по умолчанию `False`).

**Возвращает:**
- `SearchFormData`: Объект с данными формы поиска.

**Исключения:**
- `RuTrackerRequestError`: Если запрос на получение формы завершился ошибкой или сессия не инициализирована.
- `RuTrackerParsingError`: Если произошла ошибка при парсинге формы.

**Пример:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    form_data = await client.get_search_form()
    
    # Просмотр групп разделов
    for group in form_data.forum_groups:
        print(f"{group.name}: {len(group.sections)} разделов")
    
    # Принудительное обновление
    form_data = await client.get_search_form(force_refresh=True)
```

---

### Аутентификация

#### `async auth() -> None`

Асинхронно аутентифицирует пользователя на сайте RuTracker. Обычно вызывается автоматически при инициализации сессии.

**Исключения:**
- `RuTrackerAuthError`: Если статус-код ответа не 200, аутентификация не удалась, или обнаружена капча.

**Пример:**
```python
client = AsyncRuTrackerClient("login", "password")
await client.init()  # auth вызывается автоматически
```

---

### Управление сессией

#### `async close() -> None`

Закрывает асинхронную сессию. Вызывается автоматически при использовании контекстного менеджера.

**Пример:**
```python
client = AsyncRuTrackerClient("login", "password")
await client.init()
# ... использование клиента ...
await client.close()  # Закрыть сессию вручную
```

---

### Контекстный менеджер

Класс `AsyncRuTrackerClient` поддерживает использование в качестве асинхронного контекстного менеджера:

```python
async with AsyncRuTrackerClient("login", "password") as client:
    results = await client.search("query")
    # Сессия автоматически закроется после выхода из блока
```

---

## Модели данных

### SearchResult

Модель результата поиска, содержащая следующую информацию:

| Поле | Тип | Описание |
|------|-----|----------|
| `topic_id` | `int` | Идентификатор топика |
| `approved` | `str` | Статус проверки результата |
| `category` | `str` | Категория, в которой размещён результат |
| `category_url` | `Optional[str]` | URL категории |
| `title` | `str` | Название результата |
| `title_url` | `Optional[str]` | URL страницы результата |
| `author` | `str` | Автор результата |
| `author_url` | `Optional[str]` | URL страницы автора |
| `size` | `float` | Размер файла |
| `unit` | `str` | Единица измерения размера файла ('bytes', 'KB', 'MB', 'GB') |
| `download_url` | `str` | URL для скачивания файла |
| `seedmed` | `int` | Количество сидов |
| `leechmed` | `int` | Количество личеров |
| `download_counter` | `int` | Счётчик скачиваний |
| `added` | `str` | Дата и время добавления результата |

**Пример:**
```python
result = SearchResult(
    topic_id=12345,
    approved="проверено",
    category="Фильмы",
    title="Test Movie",
    author="Author",
    size=1.5,
    unit="GB",
    download_url="https://rutracker.org/forum/dl.php?t=12345",
    seedmed=10,
    leechmed=5,
    download_counter=100,
    added="01-01-2021 00:00:00"
)

print(result.title)  # "Test Movie"
print(f"{result.size} {result.unit}")  # "1.5 GB"
```

### SearchFormData

Модель данных формы поиска, содержащая:

| Поле | Тип | Описание |
|------|-----|----------|
| `forum_groups` | `List[ForumGroup]` | Список групп разделов форума |
| `sort_options` | `List[SortOption]` | Список опций сортировки |
| `sort_directions` | `List[SortDirection]` | Список направлений сортировки |
| `time_filter_options` | `List[TimeFilterOption]` | Список опций фильтра по времени |
| `forum_field_name` | `str` | Имя поля формы для разделов форума |

#### ForumGroup

Группа разделов форума:

| Поле | Тип | Описание |
|------|-----|----------|
| `name` | `str` | Название группы разделов |
| `sections` | `List[ForumSection]` | Список разделов в группе |

#### ForumSection

Раздел форума:

| Поле | Тип | Описание |
|------|-----|----------|
| `id` | `int` | Идентификатор раздела |
| `name` | `str` | Название раздела |
| `parent_id` | `Optional[int]` | ID родительского раздела |
| `is_root` | `bool` | Является ли раздел корневым |
| `has_subforums` | `bool` | Есть ли у раздела подразделы |

#### SortOption

Опция сортировки:

| Поле | Тип | Описание |
|------|-----|----------|
| `value` | `int` | Значение опции сортировки |
| `name` | `str` | Название опции сортировки |
| `form_field_name` | `str` | Имя поля формы для POST-запроса |
| `is_selected` | `bool` | Выбрана ли опция по умолчанию |

#### SortDirection

Направление сортировки:

| Поле | Тип | Описание |
|------|-----|----------|
| `value` | `int` | Значение направления (1 - по возрастанию, 2 - по убыванию) |
| `name` | `str` | Название направления сортировки |
| `form_field_name` | `str` | Имя поля формы для POST-запроса |
| `is_selected` | `bool` | Выбрано ли направление по умолчанию |

#### TimeFilterOption

Опция фильтра по времени:

| Поле | Тип | Описание |
|------|-----|----------|
| `value` | `int` | Значение фильтра по времени |
| `name` | `str` | Название фильтра по времени |
| `form_field_name` | `str` | Имя поля формы для POST-запроса |
| `is_selected` | `bool` | Выбрана ли опция по умолчанию |

---

## Исключения

Библиотека использует следующую иерархию исключений:

### RuTrackerException

Базовое исключение для всех ошибок библиотеки. Все остальные исключения наследуются от него.

### RuTrackerAuthError

Ошибки аутентификации.

**Возможные причины:**
- Неверный логин или пароль
- Обнаружена капча
- Отсутствуют cookies после аутентификации
- Ошибка при выполнении запроса аутентификации

**Пример:**
```python
from py_rutracker import RuTrackerClient
from py_rutracker.exceptions import RuTrackerAuthError

try:
    client = RuTrackerClient("wrong_login", "wrong_password")
except RuTrackerAuthError as e:
    print(f"Ошибка аутентификации: {e}")
```

### RuTrackerRequestError

Ошибки HTTP-запросов.

**Возможные причины:**
- Неожиданный статус-код ответа (не 200)
- Необходима повторная аутентификация
- Ошибка сети при выполнении запроса
- Сессия не инициализирована (для асинхронного клиента)

**Пример:**
```python
from py_rutracker.exceptions import RuTrackerRequestError

try:
    results = client.search("query")
except RuTrackerRequestError as e:
    print(f"Ошибка запроса: {e}")
```

### RuTrackerParsingError

Ошибки парсинга HTML.

**Возможные причины:**
- Изменение структуры HTML на сайте RuTracker
- Некорректный HTML в ответе сервера
- Ошибка при извлечении данных из HTML

**Пример:**
```python
from py_rutracker.exceptions import RuTrackerParsingError

try:
    results = client.search("query")
except RuTrackerParsingError as e:
    print(f"Ошибка парсинга: {e}")
```

### RuTrackerDownloadError

Ошибки скачивания торрент-файла.

**Возможные причины:**
- Передан недопустимый параметр (не int и не валидный URL)
- Файл с указанным ID не найден
- Отсутствует заголовок Content-Disposition в ответе

**Пример:**
```python
from py_rutracker.exceptions import RuTrackerDownloadError

try:
    torrent = client.get_torrent("invalid_id")
except RuTrackerDownloadError as e:
    print(f"Ошибка скачивания: {e}")
```

---

## Дополнительная информация

### Кеширование формы поиска

Данные формы поиска автоматически кешируются на 24 часа. Это позволяет уменьшить количество запросов к серверу и ускорить работу приложения.

Для принудительного обновления кеша используйте параметр `force_refresh=True`:

```python
# Обновить кеш принудительно
form_data = client.get_search_form(force_refresh=True)
```

### Обработка ошибок

Рекомендуется всегда обрабатывать исключения при работе с библиотекой:

```python
from py_rutracker import RuTrackerClient
from py_rutracker.exceptions import (
    RuTrackerAuthError,
    RuTrackerRequestError,
    RuTrackerParsingError,
    RuTrackerDownloadError
)

try:
    client = RuTrackerClient("login", "password")
    results = client.search("query")
    if results:
        client.download(results[0].topic_id)
except RuTrackerAuthError:
    print("Ошибка аутентификации")
except RuTrackerRequestError:
    print("Ошибка запроса")
except RuTrackerParsingError:
    print("Ошибка парсинга")
except RuTrackerDownloadError:
    print("Ошибка скачивания")
```

