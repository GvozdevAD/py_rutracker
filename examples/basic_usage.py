"""
Пример базового использования синхронного клиента RuTracker.
"""
import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
PROXY = os.getenv("PROXY", None)  #'http://<PROXY_IP_ADDRESS>:<PROXY_PORT>'  Опционально

from py_rutracker import RuTrackerClient

# Создание клиента с вашими учетными данными
client = RuTrackerClient(LOGIN, PASSWORD, PROXY)

# Поиск раздач по запросу
results = client.search_all_pages("Static-X")

# Вывод информации о каждой раздаче
for torrent in results:
    print(torrent)

# Скачивание торрент-файла
if results:
    topic_id = results[0].topic_id

    # Вариант 1: Использование метода download для автоматического сохранения
    file_path = client.download(topic_id, save_path="./torrents")
    print(f"Торрент сохранен: {file_path}")

    # Вариант 2: Использование get_torrent для получения байтов (если нужна дополнительная обработка)
    # bytes_data = client.get_torrent(topic_id)
    # with open(f"{topic_id}.torrent", "wb") as file:
    #     file.write(bytes_data)
