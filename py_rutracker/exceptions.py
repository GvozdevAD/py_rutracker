class RuTrackerException(Exception):
    """ Основное исключение для ошибок """

class RuTrackerAuthError(RuTrackerException):
    """ Исключение для ошибок аутентификации """

class RuTrackerRequestError(RuTrackerException):
    """ Исключение для ошибок HTTP-запросов """

class RuTrackerParsingError(RuTrackerException):
    """ Исключение для ошибок парсинга """

class RuTrackerDownloadError(RuTrackerException):
    """ Исключение для ошибки скачивания торент файла """