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
- [Документация](#документация)
  - [Методы класса `RuTrackerClient`](#методы-класса-rutrackerclient)
    - `search`
    - `search_all_pages`
    - `download`
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
        venv\Scripts\activate
        ```
    * На macOS и Linux:
        ```sh
        source venv/bin/activate
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
          bytes_data = await client.download(results[0].download_url)
          with open(f"{results[0].topic_id}.torrent", "wb") as file:
               file.write(bytes_data)

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
```python
from py_rutracker import RuTrackerClient

with RuTrackerClient("your_login", "your_password") as client:
     results = client.search_all_pages("Static-X")
     topic_id = results[0].topic_id
     bytes_data = client.download(topic_id)
     with open(f"{topic_id}.torrent", "wb") as file:
          file.write(bytes_data)
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
    
    
## Примечания

* Замените "your_login" и "your_password" на ваши действительные учетные данные RuTracker.
* Укажите прокси в словаре, если ваш запрос требует использования прокси. Если прокси не требуется, вы можете не указывать этот параметр.
* Библиотека использует неофициальный API RuTracker и может не работать в случае изменений на сайте.