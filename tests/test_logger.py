import logging

import pytest

from py_rutracker.logger import RuTrackerLogger, configure_logger, get_logger


class TestRuTrackerLogger:
    """Тесты для класса RuTrackerLogger."""
    
    def test_singleton_pattern(self):
        """Тест паттерна Singleton."""
        logger1 = RuTrackerLogger()
        logger2 = RuTrackerLogger()
        assert logger1 is logger2
    
    def test_parse_log_level_string(self):
        """Тест парсинга уровня логирования из строки."""
        logger = RuTrackerLogger()
        assert logger._parse_log_level("DEBUG") == logging.DEBUG
        assert logger._parse_log_level("INFO") == logging.INFO
        assert logger._parse_log_level("WARNING") == logging.WARNING
        assert logger._parse_log_level("ERROR") == logging.ERROR
        assert logger._parse_log_level("CRITICAL") == logging.CRITICAL
    
    def test_parse_log_level_int(self):
        """Тест парсинга уровня логирования из int."""
        logger = RuTrackerLogger()
        assert logger._parse_log_level(logging.DEBUG) == logging.DEBUG
        assert logger._parse_log_level(logging.INFO) == logging.INFO
    
    def test_parse_log_level_invalid(self):
        """Тест парсинга невалидного уровня."""
        logger = RuTrackerLogger()
        with pytest.raises(ValueError):
            logger._parse_log_level("INVALID")
    
    def test_get_logger(self):
        """Тест получения логгера."""
        logger = RuTrackerLogger()
        log = logger.get_logger()
        assert isinstance(log, logging.Logger)
        assert log.name == "py_rutracker"
    
    def test_get_logger_with_name(self):
        """Тест получения логгера с именем."""
        logger = RuTrackerLogger()
        log = logger.get_logger("test_module")
        assert isinstance(log, logging.Logger)
        assert "test_module" in log.name
    
    def test_logger_methods(self, caplog):
        """Тест методов логирования."""
        logger = RuTrackerLogger()
        logger.configure(level="DEBUG")
        
        logger.debug("Debug message")
        logger.info("Info message")
        logger.warning("Warning message")
        logger.error("Error message")
        logger.critical("Critical message")
        
        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
        assert "Critical message" in caplog.text
    
    def test_configure_logger(self):
        """Тест настройки логгера."""
        logger = RuTrackerLogger()
        logger.configure(level="INFO")
        log = logger.get_logger()
        assert log.level == logging.INFO
    
    def test_configure_logger_with_file(self, temp_dir):
        """Тест настройки логгера с записью в файл."""
        log_file = temp_dir / "test.log"
        logger = RuTrackerLogger()
        logger.configure(level="DEBUG", log_to_file=True, log_file_path=str(log_file))
        
        logger.info("Test message")
        
        assert log_file.exists()
        assert "Test message" in log_file.read_text()


class TestGetLogger:
    """Тесты для функции get_logger."""
    
    def test_get_logger_function(self):
        """Тест функции get_logger."""
        log = get_logger()
        assert isinstance(log, logging.Logger)
    
    def test_get_logger_with_name(self):
        """Тест функции get_logger с именем."""
        log = get_logger("test")
        assert isinstance(log, logging.Logger)
        assert "test" in log.name


class TestConfigureLogger:
    """Тесты для функции configure_logger."""
    
    def test_configure_logger_function(self):
        """Тест функции configure_logger."""
        configure_logger(level="DEBUG")
        log = get_logger()
        assert log.level == logging.DEBUG
    
    def test_configure_logger_with_file(self, temp_dir):
        """Тест функции configure_logger с файлом."""
        log_file = temp_dir / "configure_test.log"
        configure_logger(
            level="INFO",
            log_to_file=True,
            log_file_path=str(log_file)
        )
        
        log = get_logger()
        log.info("Configure test message")
        
        assert log_file.exists()
        assert "Configure test message" in log_file.read_text()
    
    def test_configure_logger_env_level(self, monkeypatch):
        """Тест использования уровня из переменной окружения."""
        monkeypatch.setenv("PY_RUTRACKER_LOG_LEVEL", "DEBUG")
        logger = RuTrackerLogger()
        logger._logger = None
        logger._setup_logger()
        log = logger.get_logger()
        assert log.level == logging.DEBUG

