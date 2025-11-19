from typing import Optional, Union


class RuTrackerException(Exception):
    """
    Основное исключение для ошибок библиотеки py_rutracker.
    
    Все остальные исключения наследуются от этого класса.
    """

    def __init__(self, message: str, **context):
        """
        Инициализирует исключение с сообщением и контекстной информацией.
        
        :param message: Сообщение об ошибке.
        :param context: Дополнительная контекстная информация (URL, статус-код, параметры и т.д.).
        """
        super().__init__(message)
        self.message = message
        self.context = context or {}

    def __str__(self) -> str:
        """Возвращает строковое представление исключения с контекстом."""
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{self.message} ({context_str})"
        return self.message


class RuTrackerAuthError(RuTrackerException):
    """
    Исключение для ошибок аутентификации.
    
    Используется когда:
    - Неверный логин или пароль
    - Обнаружена капча
    - Отсутствуют cookies после аутентификации
    - Ошибка при выполнении запроса аутентификации
    """

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        **context
    ):
        """
        Инициализирует исключение аутентификации.
        
        :param message: Сообщение об ошибке.
        :param url: URL запроса аутентификации (опционально).
        :param status_code: HTTP статус-код ответа (опционально).
        :param context: Дополнительная контекстная информация.
        """
        context_dict = context.copy()
        if url is not None:
            context_dict["url"] = url
        if status_code is not None:
            context_dict["status_code"] = status_code
        super().__init__(message, **context_dict)
        self.url = url
        self.status_code = status_code


class RuTrackerRequestError(RuTrackerException):
    """
    Исключение для ошибок HTTP-запросов.
    
    Используется когда:
    - Неожиданный статус-код ответа (не 200)
    - Необходима повторная аутентификация
    - Ошибка сети при выполнении запроса
    - Сессия не инициализирована (для асинхронного клиента)
    """

    def __init__(
        self,
        message: str,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        params: Optional[dict] = None,
        **context
    ):
        """
        Инициализирует исключение запроса.
        
        :param message: Сообщение об ошибке.
        :param url: URL запроса (опционально).
        :param status_code: HTTP статус-код ответа (опционально).
        :param params: Параметры запроса (опционально).
        :param context: Дополнительная контекстная информация.
        """
        context_dict = context.copy()
        if url is not None:
            context_dict["url"] = url
        if status_code is not None:
            context_dict["status_code"] = status_code
        if params is not None:
            context_dict["params"] = params
        super().__init__(message, **context_dict)
        self.url = url
        self.status_code = status_code
        self.params = params


class RuTrackerParsingError(RuTrackerException):
    """
    Исключение для ошибок парсинга HTML.
    
    Используется когда:
    - Изменение структуры HTML на сайте RuTracker
    - Некорректный HTML в ответе сервера
    - Ошибка при извлечении данных из HTML
    """

    def __init__(
        self,
        message: str,
        html_snippet: Optional[str] = None,
        selector: Optional[str] = None,
        **context
    ):
        """
        Инициализирует исключение парсинга.
        
        :param message: Сообщение об ошибке.
        :param html_snippet: Фрагмент HTML, который вызвал ошибку (опционально).
        :param selector: CSS-селектор, который использовался (опционально).
        :param context: Дополнительная контекстная информация.
        """
        context_dict = context.copy()
        if html_snippet is not None:
            # Ограничиваем длину фрагмента для читаемости
            snippet = html_snippet[:200] + "..." if len(html_snippet) > 200 else html_snippet
            context_dict["html_snippet"] = snippet
        if selector is not None:
            context_dict["selector"] = selector
        super().__init__(message, **context_dict)
        self.html_snippet = html_snippet
        self.selector = selector


class RuTrackerDownloadError(RuTrackerException):
    """
    Исключение для ошибок скачивания торрент-файла.
    
    Используется когда:
    - Передан недопустимый параметр (не int и не валидный URL)
    - Файл с указанным ID не найден
    - Отсутствует заголовок Content-Disposition в ответе
    """

    def __init__(
        self,
        message: str,
        topic_id_or_url: Optional[Union[int, str]] = None,
        url: Optional[str] = None,
        status_code: Optional[int] = None,
        **context
    ):
        """
        Инициализирует исключение скачивания.
        
        :param message: Сообщение об ошибке.
        :param topic_id_or_url: Идентификатор топика или URL, который вызвал ошибку (опционально).
        :param url: URL запроса (опционально).
        :param status_code: HTTP статус-код ответа (опционально).
        :param context: Дополнительная контекстная информация.
        """
        context_dict = context.copy()
        if topic_id_or_url is not None:
            context_dict["topic_id_or_url"] = topic_id_or_url
        if url is not None:
            context_dict["url"] = url
        if status_code is not None:
            context_dict["status_code"] = status_code
        super().__init__(message, **context_dict)
        self.topic_id_or_url = topic_id_or_url
        self.url = url
        self.status_code = status_code


class RuTrackerValidationError(RuTrackerException):
    """
    Исключение для ошибок валидации входных данных.
    
    Используется когда:
    - Невалидный логин или пароль (пустые, слишком короткие)
    - Невалидный заголовок поиска (пустой, слишком длинный)
    - Невалидный номер страницы (меньше 1, не целое число)
    """

    def __init__(
        self,
        message: str,
        field_name: Optional[str] = None,
        field_value: Optional[Union[str, int]] = None,
        **context
    ):
        """
        Инициализирует исключение валидации.
        
        :param message: Сообщение об ошибке.
        :param field_name: Название поля, которое не прошло валидацию (опционально).
        :param field_value: Значение поля, которое не прошло валидацию (опционально).
        :param context: Дополнительная контекстная информация.
        """
        context_dict = context.copy()
        if field_name is not None:
            context_dict["field_name"] = field_name
        if field_value is not None:
            context_dict["field_value"] = field_value
        super().__init__(message, **context_dict)
        self.field_name = field_name
        self.field_value = field_value
