class RuTrackerException(Exception):
    """Основное исключение для ошибок RuTracker."""

class RuTrackerAuthException(RuTrackerException):
    """Исключение для ошибок аутентификации RuTracker."""

class RuTrackerRequestException(RuTrackerException):
    """Исключение для ошибок HTTP-запросов RuTracker."""

class RuTrackerParsingException(RuTrackerException):
    """Исключение для ошибок парсинга RuTracker."""
