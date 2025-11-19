import re
from typing import Optional

from bs4 import BeautifulSoup

from ..enums import Url
from ..logger import get_logger
from ..models.search import SearchResult
from ..utils.helpers import convert_unix_to_local_time, format_size, is_integer

logger = get_logger(__name__)


class ParsingPage:
    @staticmethod
    def search(
        html: str, return_dict_format: bool = False
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
            leechmed_text = info_row[6].text.strip()
            download_counter_text = info_row[7].text.strip()
            added = convert_unix_to_local_time(int(info_row[8]["data-ts_text"]))

            result = {
                "topic_id": topic_id,
                "approved": approved or "",
                "category": category,
                "category_url": category_url or None,
                "title": title,
                "title_url": title_url or None,
                "author": author,
                "author_url": author_url or None,
                "size": size,
                "unit": unit,
                "download_url": download_url,
                "seedmed": seedmed_text,
                "leechmed": leechmed_text,
                "download_counter": download_counter_text,
                "added": added,
            }
            if return_dict_format:
                results.append(result)
            else:
                try:
                    results.append(SearchResult(**result))
                except Exception as e:
                    logger.warning(
                        f"Ошибка валидации результата поиска (topic_id={result.get('topic_id', 'unknown')}): {e}. "
                        f"Результат пропущен."
                    )
                    continue
        return results
    
    @staticmethod
    def extract_search_id(html: str) -> Optional[str]:
        """
        Извлекает search_id из HTML ответа поиска.
        
        Приоритет поиска:
        1. JavaScript переменная PG_BASE_URL: 'tracker.php?search_id=XXXXX'
        2. JavaScript переменная search_id в любом виде
        3. Ссылки пагинации с классом pg: href="tracker.php?search_id=XXXXX&start=..."
        4. Любые ссылки с search_id в href
        5. Скрытые поля формы: <input type="hidden" name="search_id" value="...">
        6. Поиск в любых атрибутах data-* с search_id
        7. Поиск в тексте страницы через регулярное выражение
        
        :param html: HTML контент страницы с результатами поиска.
        :return: search_id или None, если не найден.
        """
        if not html:
            return None
        
        pg_base_url_pattern = r"PG_BASE_URL:\s*['\"]tracker\.php\?search_id=([^'\"]+)['\"]"
        match = re.search(pg_base_url_pattern, html)
        if match:
            search_id = match.group(1)
            logger.debug(f"search_id найден в PG_BASE_URL: {search_id}")
            return search_id
        
        js_search_id_patterns = [
            r"search_id\s*[:=]\s*['\"]([^'\"]+)['\"]",
            r"['\"]search_id['\"]\s*[:=]\s*['\"]([^'\"]+)['\"]",
            r"search_id\s*=\s*['\"]([^'\"]+)['\"]",
        ]
        for pattern in js_search_id_patterns:
            match = re.search(pattern, html)
            if match:
                search_id = match.group(1)
                if len(search_id) > 5 and ' ' not in search_id:
                    logger.debug(f"search_id найден в JavaScript переменной: {search_id}")
                    return search_id
        
        soup = BeautifulSoup(html, features="lxml")
        
        pagination_links = soup.find_all("a", class_="pg")
        for link in pagination_links:
            href = link.get("href", "")
            if "search_id=" in href:
                search_id_match = re.search(r"search_id=([^&]+)", href)
                if search_id_match:
                    search_id = search_id_match.group(1)
                    logger.debug(f"search_id найден в ссылке пагинации: {search_id}")
                    return search_id
        
        all_links = soup.find_all("a", href=re.compile(r"search_id="))
        for link in all_links:
            href = link.get("href", "")
            search_id_match = re.search(r"search_id=([^&]+)", href)
            if search_id_match:
                search_id = search_id_match.group(1)
                logger.debug(f"search_id найден в ссылке: {search_id}")
                return search_id
        
        hidden_inputs = soup.find_all("input", type="hidden", attrs={"name": "search_id"})
        for input_field in hidden_inputs:
            search_id = input_field.get("value")
            if search_id:
                logger.debug(f"search_id найден в скрытом поле формы: {search_id}")
                return search_id
        
        all_elements = soup.find_all(True)
        for element in all_elements:
            if hasattr(element, 'attrs') and element.attrs:
                for attr_name, attr_value in element.attrs.items():
                    if (attr_name.startswith('data-') or "search_id=" in str(attr_value)):
                        if isinstance(attr_value, str) and "search_id=" in attr_value:
                            search_id_match = re.search(r"search_id=([^&\s\"']+)", attr_value)
                            if search_id_match:
                                search_id = search_id_match.group(1)
                                logger.debug(f"search_id найден в атрибуте {attr_name}: {search_id}")
                                return search_id

        fallback_pattern = r"tracker\.php\?search_id=([^&\s\"'<>]+)"
        matches = re.findall(fallback_pattern, html)
        if matches:
            search_id = matches[0]
            if len(search_id) > 5:
                logger.debug(f"search_id найден через fallback паттерн: {search_id}")
                return search_id
        
        logger.debug("search_id не найден в HTML")
        return None
