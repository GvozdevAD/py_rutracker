from pydantic import BaseModel, Field, field_validator
from typing import Optional


class SearchResult(BaseModel):
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
    topic_id: int = Field(..., description="Идентификатор результата", gt=0)
    approved: str = Field(..., description="Статус проверки результата")
    category: str = Field(..., description="Категория, в которой размещён результат")
    category_url: Optional[str] = Field(None, description="URL категории")
    title: str = Field(..., description="Название результата")
    title_url: Optional[str] = Field(None, description="URL страницы результата")
    author: str = Field(..., description="Автор результата")
    author_url: Optional[str] = Field(None, description="URL страницы автора")
    size: float = Field(..., description="Размер файла", ge=0)
    unit: str = Field(..., description="Единица измерения размера файла")
    download_url: str = Field(..., description="URL для скачивания файла")
    seedmed: int = Field(default=0, description="Количество сидов", ge=0)
    leechmed: int = Field(default=0, description="Количество личеров", ge=0)
    download_counter: int = Field(default=0, description="Счётчик скачиваний", ge=0)
    added: str = Field(..., description="Дата и время добавления результата")
    
    @field_validator('unit')
    @classmethod
    def validate_unit(cls, v: str) -> str:
        """Валидация единицы измерения."""
        allowed_units = ['bytes', 'KB', 'MB', 'GB', 'TB']
        if v not in allowed_units:
            return v
        return v
    
    @field_validator('seedmed', 'leechmed', 'download_counter', mode='before')
    @classmethod
    def validate_non_negative(cls, v):
        """Валидация неотрицательных значений с автоматическим преобразованием строк."""
        if isinstance(v, str):
            v = int(v) if v.strip().isdigit() else 0
        if v is None:
            return 0
        return max(0, int(v))
    
    @field_validator('category_url', 'title_url', 'author_url', mode='before')
    @classmethod
    def validate_url(cls, v):
        """Валидация URL - если пустая строка, возвращаем None."""
        if v == "" or v is None:
            return None
        return v
    
    def __str__(self) -> str:
        return (
            f"Topic ID: {self.topic_id}\n" 
            f"Title: {self.title}\n"
            f"Author: {self.author}\n"
            f"Category: {self.category}\n"
            f"Size: {self.size} {self.unit}\n"
            f"Download URL: {self.download_url}\n"
            f"Added: {self.added}\n"
            f"Seed: {self.seedmed}\n"
            f"Leech: {self.leechmed}\n"
            f"Download Counter: {self.download_counter}"
        )
    
    def model_dump_dict(self) -> dict:
        """
        Возвращает словарь с данными модели.
        Удобно для обратной совместимости с return_search_dict=True.
        """
        return self.model_dump()
    
    class Config:
        """Конфигурация Pydantic модели."""
        use_enum_values = True
        validate_assignment = True


class ResponseRuTracker(BaseModel):
    """
    Класс для хранения ответа от RuTracker.
    """
    success: bool = Field(..., description="Успешность операции")
    results: list[SearchResult] = Field(default_factory=list, description="Список результатов поиска")
    
    class Config:
        """Конфигурация Pydantic модели."""
        use_enum_values = True
        validate_assignment = True
