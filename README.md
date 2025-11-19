# Py_RuTracker

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[English](docs/README_EN.md) | **Русский**

Py_RuTracker — это Python-библиотека для работы с RuTracker, популярным российским торрент-трекером. Библиотека предоставляет удобный и простой в использовании API для поиска раздач, получения информации о торрентах и их скачивания.

## Основные возможности

- 🔍 **Поиск раздач** — поиск по названию с поддержкой пагинации и фильтрации
- ⬇️ **Скачивание торрентов** — автоматическое сохранение `.torrent` файлов или получение байтов для обработки
- 📋 **Работа с формой поиска** — получение разделов форума, опций сортировки и фильтров по времени
- ⚡ **Синхронный и асинхронный API** — выбор подходящего варианта для вашего проекта
- 🚀 **Производительность** — асинхронный клиент выполняет запросы параллельно для максимальной скорости
- 💾 **Кеширование** — автоматическое кеширование данных формы поиска для уменьшения нагрузки на сервер
- 📝 **Логирование** — настраиваемое логирование для отладки и мониторинга
- 🛡️ **Обработка ошибок** — детальные исключения для всех типов ошибок
- 🔐 **Поддержка прокси** — работа через прокси-серверы

## Содержание

- [Установка](#установка)
- [Быстрый старт](#быстрый-старт)
- [Основные возможности](#основные-возможности)
- [Документация](#документация)
- [Примеры](#примеры)
- [Логирование](#логирование)
- [Технологии](#технологии)
- [Внесение вклада](#внесение-вклада)
- [Примечания](#примечания)


## Установка 

Вы можете установить библиотеку несколькими способами.

### Установка с PyPI

Для установки библиотеки используйте `pip`:

```sh
pip install py-rutracker-client
```

### Установка из исходников

#### Вариант 1: Использование Poetry (рекомендуется)

Проект использует Poetry для управления зависимостями. После клонирования репозитория:

1. Клонируйте репозиторий:
    ```sh
    git clone https://github.com/GvozdevAD/py_rutracker
    cd py_rutracker
    ```

2. Установите зависимости с помощью Poetry:
    ```sh
    poetry install --no-root
    ```

3. Активируйте виртуальное окружение Poetry:
    ```sh
    poetry shell
    ```

#### Вариант 2: Использование venv и pip

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

## Быстрый старт

### Синхронный клиент

```python
from py_rutracker import RuTrackerClient

# Создание клиента
client = RuTrackerClient("your_login", "your_password")

# Поиск раздач
results = client.search_all_pages("Static-X")

# Вывод результатов
for torrent in results:
    print(torrent)

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
        results = await client.search_all_pages("rammstein")
        if results:
            file_path = await client.download(
                results[0].topic_id,
                save_path="./torrents"
            )
            print(f"Торрент сохранен: {file_path}")

asyncio.run(main())
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

## Документация

Полная документация по API доступна в файле [docs/DOCUMENTATION.md](docs/DOCUMENTATION.md) (на русском) или [docs/DOCUMENTATION_EN.md](docs/DOCUMENTATION_EN.md) (in English).

Документация включает:
- Подробное описание всех методов `RuTrackerClient` и `AsyncRuTrackerClient`
- Описание моделей данных (`SearchResult`, `SearchFormData` и др.)
- Описание исключений и их обработки
- Дополнительную информацию о кешировании и работе библиотеки

## Примеры

Подробные примеры использования библиотеки доступны в файле [docs/EXAMPLES.md](docs/EXAMPLES.md) (на русском) или [docs/EXAMPLES_EN.md](docs/EXAMPLES_EN.md) (in English).

В папке `examples/` находятся готовые примеры кода:

- **`basic_usage.py`** — базовое использование синхронного клиента
- **`async_usage.py`** — пример использования асинхронного клиента
- **`get_search_form.py`** — работа с формой поиска (синхронный клиент)
- **`get_search_form_async.py`** — работа с формой поиска (асинхронный клиент)
- **`logging_example.py`** — примеры настройки логирования

Вы можете запустить любой пример:

```bash
# Установите переменные окружения перед запуском
export LOGIN="your_login"
export PASSWORD="your_password"
export PROXY="http://proxy:8080"  # Опционально

# Запуск примеров
python examples/basic_usage.py
python examples/async_usage.py
python examples/get_search_form.py
python examples/get_search_form_async.py
python examples/logging_example.py
```  

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