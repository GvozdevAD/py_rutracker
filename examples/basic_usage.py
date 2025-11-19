"""
Пример базового использования синхронного клиента RuTracker.
"""
from py_rutracker import RuTrackerClient

# Создание клиента с вашими учетными данными
client = RuTrackerClient("your_login", "your_password")

# Поиск раздач по запросу
results = client.search_all_pages("Static-X")

# Вывод информации о каждой раздаче
for torrent in results:
    print(torrent)

# Скачивание торрент-файла
if results:
    topic_id = results[0].topic_id
    bytes_data = client.download(topic_id)
    with open(f"{topic_id}.torrent", "wb") as file:
        file.write(bytes_data)

