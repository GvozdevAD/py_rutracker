from dataclasses import dataclass


@dataclass
class SearchResult:
    """
    Класс для хранения информации о результатах поиска на RuTracker.

    :param topic_id: Идентификатор результата.
    :param approved: Статус проверки результата.
    :param category: Категория, в которой размещён результат.
    :param category_url: URL категории, где размещён результат.
    :param title: Название результата.
    :param author: Автор результата.
    :param author_url: URL страницы автора.
    :param size: Размер файла.
    :param unit: Единица измерения размера файла (например, 'GB', 'MB').
    :param download_url: URL для скачивания файла.
    :param seedmed: Количество сидов для результата.
    :param leechmed: Количество личеров для результата.
    :param download_counter: Счётчик скачиваний результата.
    :param added: Дата и время добавления результата.
    """
    topic_id: int
    approved: str
    category: str
    category_url: str
    title: str
    title_url: str
    author: str
    author_url: str
    size: float
    unit: str
    download_url: str
    seedmed: int
    leechmed: int
    download_counter: int
    added: str
    
    def __str__(self):
        return (
            f"Topic ID: {self.topic_id}\n" 
            f"Title: {self.title}\n"
            f"Author: {self.author}\n"
            f"Сategory: {self.category}\n"
            f"Size: {self.size} {self.unit}\n"
            f"Download URL: {self.download_url}\n"
            f"Added: {self.added}\n"
            f"Seed: {self.seedmed}\n"
            f"Leech: {self.leechmed}\n"
            f"Download Counter: {self.download_counter}"
        )


@dataclass
class ResponseRuTracker:
    """
    """
    success: bool
    results: SearchResult
    
