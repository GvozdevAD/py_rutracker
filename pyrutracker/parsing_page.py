from bs4 import BeautifulSoup

from .datacls import SearchResult
from .enums import Url
from .utils import (
    format_size,
    convert_unix_to_local_time,
    is_integer
)

class ParsingPage:
    @staticmethod
    def search(
            html: str,
            return_dict_format: bool = False
    ) -> list[SearchResult | dict]:
        """Парсит HTML и возвращает результаты поиска в указанном формате."""
        results = []

        soup = BeautifulSoup(html, features="lxml")
        table = soup.find("table", id="tor-tbl")
        if not table:
            return results
        rows = table.find("tbody").find_all("tr")
        
        for row in rows:
            info_row = row.find_all("td")[1:]
            if not info_row:
                break
            
            approved = info_row[0].get("title")
            
            
            if approved == "закрыто":
                continue

            category = info_row[1].find("a").text
            category_url = info_row[1].find("a").get("href")
            if category_url: 
                category_url = f"{Url.FORUM.value}/{category_url}"
            
            title = info_row[2].find("a").text
            title_url = info_row[2].find("a").get("href", "")
            if title_url:
                title_url = f"{Url.FORUM.value}/{title_url}"
            topic_id = int(info_row[2].find("a").get("data-topic_id"))

            
            author = info_row[3].find("a").text
            author_url = info_row[3].find("a").get("href")
            if author_url:
                author_url = f"{Url.FORUM.value}/{author_url}"

            size, unit = format_size(int(info_row[4]["data-ts_text"]))
            
            download_url = info_row[4].find("a").get("href")
            if download_url:
                download_url = f"{Url.FORUM.value}/{download_url}"

            seedmed_text = info_row[5].text.strip()
            seedmed = int(seedmed_text) if is_integer(seedmed_text) else 0
            
            leechmed = int(info_row[6].text)
            download_counter = int(info_row[7].text)
            added = convert_unix_to_local_time(int(info_row[8]["data-ts_text"]))

            result = {
                    "topic_id": topic_id,
                    "approved": approved, 
                    "category": category, 
                    "category_url": category_url, 
                    "title": title,
                    "title_url": title_url,
                    "author": author,
                    "author_url": author_url,
                    "size": size,
                    "unit": unit,
                    "download_url": download_url,
                    "seedmed": seedmed,
                    "leechmed": leechmed,
                    "download_counter": download_counter,
                    "added": added
                }
            if return_dict_format:
                results.append(result)
            else:
                results.append(
                    SearchResult(** result)
                )
        return results

    @staticmethod
    def viewtopic(
            html: str,
    ):
        """ """