from datetime import datetime, timedelta, timezone


def format_size(bytes: int) -> tuple[float, str]:
    """
    Форматирует размер в байтах и возвращает кортеж с двумя значениями:
    преобразованное значение и единица измерения (KB, MB, GB).

    :param bytes: Размер в байтах.
    :return: Кортеж с двумя элементами:
             1. Преобразованное значение размера (float).
             2. Единица измерения (str).
    """
    if bytes < 0:
        raise ValueError("Размер не может быть отрицательным")
    if bytes == 0:
        return 0.0, 'KB'
    if bytes >= 1024 ** 3:
        gigabytes = bytes / (1024 ** 3)
        return round(gigabytes, 2), 'GB'
    elif bytes >= 1024 ** 2:
        megabytes = bytes / (1024 ** 2)
        return round(megabytes, 2), 'MB'
    elif bytes >= 1024:
        kilobytes = bytes / 1024
        return round(kilobytes, 2), 'KB'
    else:
        return float(bytes), 'bytes'

def convert_unix_to_local_time(
        epoch: int, 
        offset_hours: int = 3
) -> str:
    """
    Конвертирует время в формате эпохи Unix в строку с датой и временем с учетом смещения времени.

    :param epoch: Время в формате эпохи Unix.
    :param offset_hours: Смещение времени в часах относительно UTC.
    :return: Строка с датой и временем, включая смещение времени.
    """
    dt = datetime.fromtimestamp(epoch, tz=timezone.utc)
    offset = dt + timedelta(hours=offset_hours)
    return offset.strftime('%d-%m-%Y %H:%M:%S')

def is_integer(value: str) -> bool:
    """
    Проверяет, является ли строка целым числом.
    """
    return value.isdigit()