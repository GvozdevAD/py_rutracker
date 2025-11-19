"""
Пример использования асинхронного клиента RuTracker.
"""
import asyncio
from py_rutracker.clients.async_client import AsyncRuTrackerClient

login = "your_login"
password = "your_password"
proxies = 'http://<PROXY_IP_ADDRESS>:<PROXY_PORT>'  # Опционально

async def main():
    async with AsyncRuTrackerClient(login, password, proxies) as client:
        results = await client.search_all_pages("rammstein")
        if results:
            bytes_data = await client.download(results[0].download_url)
            with open(f"{results[0].topic_id}.torrent", "wb") as file:
                file.write(bytes_data)

if __name__ == "__main__":
    asyncio.run(main())

