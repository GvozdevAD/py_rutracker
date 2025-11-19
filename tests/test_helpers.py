import pytest

from py_rutracker.utils.helpers import (convert_unix_to_local_time,
                                        format_size, is_integer)


class TestFormatSize:
    """Тесты для функции format_size."""
    
    def test_format_bytes(self):
        """Тест форматирования байтов."""
        size, unit = format_size(512)
        assert size == 512.0
        assert unit == "bytes"
    
    def test_format_kilobytes(self):
        """Тест форматирования килобайтов."""
        size, unit = format_size(2048)
        assert size == 2.0
        assert unit == "KB"
    
    def test_format_megabytes(self):
        """Тест форматирования мегабайтов."""
        size, unit = format_size(5 * 1024 * 1024)
        assert size == 5.0
        assert unit == "MB"
    
    def test_format_gigabytes(self):
        """Тест форматирования гигабайтов."""
        size, unit = format_size(3 * 1024 * 1024 * 1024)
        assert size == 3.0
        assert unit == "GB"
    
    def test_format_zero(self):
        """Тест форматирования нуля."""
        size, unit = format_size(0)
        assert size == 0.0
        assert unit == "KB"
    
    def test_format_negative_raises_error(self):
        """Тест что отрицательное значение вызывает ошибку."""
        with pytest.raises(ValueError) as exc_info:
            format_size(-1)
        assert "отрицательным" in str(exc_info.value).lower()
    
    def test_format_rounding(self):
        """Тест округления."""
        size, unit = format_size(1536)  # 1.5 KB
        assert size == 1.5
        assert unit == "KB"
        
        size, unit = format_size(1536000)  # 1.46484375 MB
        assert size == 1.46
        assert unit == "MB"


class TestConvertUnixToLocalTime:
    """Тесты для функции convert_unix_to_local_time."""
    
    def test_convert_with_default_offset(self):
        """Тест конвертации с дефолтным смещением."""
        epoch = 1609459200  # 2021-01-01 00:00:00 UTC
        result = convert_unix_to_local_time(epoch)
        assert isinstance(result, str)
        assert "2021" in result
        assert "01-01" in result
    
    def test_convert_with_custom_offset(self):
        """Тест конвертации с кастомным смещением."""
        epoch = 1609459200  # 2021-01-01 00:00:00 UTC
        result = convert_unix_to_local_time(epoch, offset_hours=5)
        assert isinstance(result, str)
        assert "2021" in result
    
    def test_convert_format(self):
        """Тест формата результата."""
        epoch = 1609459200
        result = convert_unix_to_local_time(epoch)
        # Формат: DD-MM-YYYY HH:MM:SS
        parts = result.split(" ")
        assert len(parts) == 2
        date_parts = parts[0].split("-")
        assert len(date_parts) == 3
        time_parts = parts[1].split(":")
        assert len(time_parts) == 3


class TestIsInteger:
    """Тесты для функции is_integer."""
    
    def test_is_integer_with_digits(self):
        """Тест с цифрами."""
        assert is_integer("123") is True
        assert is_integer("0") is True
        assert is_integer("999999") is True
    
    def test_is_integer_with_non_digits(self):
        """Тест с нецифровыми символами."""
        assert is_integer("abc") is False
        assert is_integer("12.34") is False
        assert is_integer("12a") is False
        assert is_integer("") is False
    
    def test_is_integer_with_negative(self):
        """Тест с отрицательным числом."""
        assert is_integer("-123") is False  # Строка с минусом не считается цифрой
    
    def test_is_integer_with_whitespace(self):
        """Тест с пробелами."""
        assert is_integer(" 123 ") is False
        assert is_integer("123 ") is False

