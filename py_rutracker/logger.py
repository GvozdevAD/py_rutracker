"""
Модуль для централизованного логирования в py_rutracker.
"""
import logging
import os
import sys
from typing import Optional, Union
from pathlib import Path


class RuTrackerLogger:
    """
    Класс для настройки и управления логированием в библиотеке py_rutracker.
    
    Предоставляет централизованное логирование с настраиваемыми уровнями,
    форматами и обработчиками.
    """
    
    _instance: Optional['RuTrackerLogger'] = None
    _logger: Optional[logging.Logger] = None
    
    def __new__(cls):
        """Реализация паттерна Singleton."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Инициализация логгера."""
        if self._logger is None:
            self._setup_logger()
    
    @staticmethod
    def _parse_log_level(level: Union[str, int]) -> int:
        """
        Преобразует строковое представление уровня логирования в константу logging.
        
        :param level: Уровень логирования (строка или int).
        :return: Константа уровня логирования из модуля logging.
        :raises ValueError: Если уровень логирования не распознан.
        """
        if isinstance(level, int):
            return level
        
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'WARN': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
            'FATAL': logging.CRITICAL,
        }
        
        level_upper = level.upper()
        if level_upper not in level_map:
            raise ValueError(
                f"Неизвестный уровень логирования: {level}. "
                f"Допустимые значения: {', '.join(level_map.keys())}"
            )
        
        return level_map[level_upper]
    
    def _setup_logger(
        self,
        name: str = "py_rutracker",
        level: Optional[Union[int, str]] = None,
        log_to_file: bool = False,
        log_file_path: Optional[str] = None,
        format_string: Optional[str] = None
    ) -> None:
        """
        Настраивает логгер с указанными параметрами.
        
        :param name: Имя логгера.
        :param level: Уровень логирования (logging.DEBUG, INFO, WARNING, ERROR, CRITICAL) или строка ('DEBUG', 'INFO', и т.д.).
                      Если None, используется значение из переменной окружения PY_RUTRACKER_LOG_LEVEL или WARNING по умолчанию.
        :param log_to_file: Флаг для записи логов в файл.
        :param log_file_path: Путь к файлу логов (если None, используется py_rutracker.log в текущей директории).
        :param format_string: Кастомный формат логов.
        """
        self._logger = logging.getLogger(name)
        
        if level is None:
            env_level = os.getenv('PY_RUTRACKER_LOG_LEVEL', 'WARNING').upper()
            level = self._parse_log_level(env_level)
        elif isinstance(level, str):
            level = self._parse_log_level(level)
        
        self._logger.setLevel(level)
        
        self._logger.handlers.clear()
        
        if format_string is None:
            format_string = (
                '%(asctime)s - %(name)s - %(levelname)s - '
                '%(filename)s:%(lineno)d - %(message)s'
            )
        
        formatter = logging.Formatter(format_string, datefmt='%Y-%m-%d %H:%M:%S')
        
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        self._logger.addHandler(console_handler)
        
        if log_to_file:
            if log_file_path is None:
                log_file_path = Path.cwd() / "py_rutracker.log"
            else:
                log_file_path = Path(log_file_path)
            
            log_file_path.parent.mkdir(parents=True, exist_ok=True)
            
            file_handler = logging.FileHandler(log_file_path, encoding='utf-8')
            file_handler.setLevel(level)
            file_handler.setFormatter(formatter)
            self._logger.addHandler(file_handler)
    
    def configure(
        self,
        level: Optional[Union[int, str]] = None,
        log_to_file: bool = False,
        log_file_path: Optional[str] = None,
        format_string: Optional[str] = None
    ) -> None:
        """
        Перенастраивает логгер с новыми параметрами.
        
        :param level: Уровень логирования (int или строка: 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
                      Если None, используется текущий уровень или значение из переменной окружения.
        :param log_to_file: Флаг для записи логов в файл.
        :param log_file_path: Путь к файлу логов.
        :param format_string: Кастомный формат логов.
        """
        if level is None:
            if self._logger:
                level = self._logger.level
            else:
                env_level = os.getenv('PY_RUTRACKER_LOG_LEVEL', 'WARNING').upper()
                level = self._parse_log_level(env_level)
        
        self._setup_logger(
            level=level,
            log_to_file=log_to_file,
            log_file_path=log_file_path,
            format_string=format_string
        )
    
    def get_logger(self, name: Optional[str] = None) -> logging.Logger:
        """
        Возвращает настроенный логгер.
        
        :param name: Имя для дочернего логгера (опционально).
        :return: Объект logging.Logger.
        """
        if self._logger is None:
            self._setup_logger()
        
        if name:
            return self._logger.getChild(name)
        return self._logger
    
    def debug(self, message: str, *args, **kwargs) -> None:
        """Логирует сообщение уровня DEBUG."""
        if self._logger:
            self._logger.debug(message, *args, **kwargs)
    
    def info(self, message: str, *args, **kwargs) -> None:
        """Логирует сообщение уровня INFO."""
        if self._logger:
            self._logger.info(message, *args, **kwargs)
    
    def warning(self, message: str, *args, **kwargs) -> None:
        """Логирует сообщение уровня WARNING."""
        if self._logger:
            self._logger.warning(message, *args, **kwargs)
    
    def error(self, message: str, *args, exc_info=None, **kwargs) -> None:
        """
        Логирует сообщение уровня ERROR.
        
        :param message: Сообщение для логирования.
        :param exc_info: Информация об исключении (кортеж или True для автоматического).
        :param kwargs: Дополнительные аргументы для логирования.
        """
        if self._logger:
            self._logger.error(message, *args, exc_info=exc_info, **kwargs)
    
    def critical(self, message: str, *args, **kwargs) -> None:
        """Логирует сообщение уровня CRITICAL."""
        if self._logger:
            self._logger.critical(message, *args, **kwargs)
    
    def exception(self, message: str, *args, **kwargs) -> None:
        """Логирует сообщение уровня ERROR с информацией об исключении."""
        if self._logger:
            self._logger.exception(message, *args, **kwargs)


_logger_instance = RuTrackerLogger()

def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Возвращает настроенный логгер.
    
    :param name: Имя для дочернего логгера (опционально).
    :return: Объект logging.Logger.
    """
    return _logger_instance.get_logger(name)


def configure_logger(
    level: Optional[Union[int, str]] = None,
    log_to_file: bool = False,
    log_file_path: Optional[str] = None,
    format_string: Optional[str] = None
) -> None:
    """
    Настраивает глобальный логгер библиотеки py_rutracker.
    
    По умолчанию логируется только WARNING и выше. Для отладки можно установить
    уровень INFO или DEBUG.
    
    Примеры использования:
        # Установить уровень INFO
        configure_logger(level='INFO')
        
        # Установить уровень DEBUG с записью в файл
        configure_logger(level=logging.DEBUG, log_to_file=True)
        
        # Использовать переменную окружения
        # export PY_RUTRACKER_LOG_LEVEL=DEBUG
    
    :param level: Уровень логирования (int из модуля logging или строка: 'DEBUG', 'INFO', 
                  'WARNING', 'ERROR', 'CRITICAL'). Если None, используется значение из 
                  переменной окружения PY_RUTRACKER_LOG_LEVEL или WARNING по умолчанию.
    :param log_to_file: Флаг для записи логов в файл.
    :param log_file_path: Путь к файлу логов. Если None и log_to_file=True, 
                          используется py_rutracker.log в текущей директории.
    :param format_string: Кастомный формат логов. Если None, используется формат по умолчанию.
    """
    _logger_instance.configure(
        level=level,
        log_to_file=log_to_file,
        log_file_path=log_file_path,
        format_string=format_string
    )

