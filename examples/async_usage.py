"""
Пример использования асинхронного клиента RuTracker.
"""

import asyncio
import os

from py_rutracker.clients.async_client import AsyncRuTrackerClient

LOGIN = os.getenv("LOGIN")
PASSWORD = os.getenv("PASSWORD")
PROXY = os.getenv("PROXY", None)  #'http://<PROXY_IP_ADDRESS>:<PROXY_PORT>'  Опционально


async def main():
    async with AsyncRuTrackerClient(LOGIN, PASSWORD, PROXY) as client:
        results = await client.search_all_pages("rammstein")
        if results:
            # Вариант 1: Использование метода download для автоматического сохранения
            file_path = await client.download(
                results[0].topic_id,
                save_path="./torrents",
                filename=f"{results[0].title[:50]}.torrent",  # Использовать название как имя файла
            )
            print(f"Торрент сохранен: {file_path}")

            # Вариант 2: Использование get_torrent для получения байтов
            # bytes_data = await client.get_torrent(results[0].topic_id)
            # with open(f"{results[0].topic_id}.torrent", "wb") as file:
            #     file.write(bytes_data)


if __name__ == "__main__":
    asyncio.run(main())
