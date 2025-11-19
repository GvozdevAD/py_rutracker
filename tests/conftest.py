import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest

pytest_plugins = ('pytest_asyncio',)


@pytest.fixture
def mock_html_search_results():
    """Фикстура с примером HTML результатов поиска."""
    return """
    <html>
    <body>
        <table id="tor-tbl">
            <tbody>
                <tr>
                    <td></td>
                    <td title="проверено"></td>
                    <td><a href="viewforum.php?f=123">Фильмы</a></td>
                    <td><a href="viewtopic.php?t=12345" data-topic_id="12345">Test Movie</a></td>
                    <td><a href="profile.php?u=1">Author</a></td>
                    <td data-ts_text="1073741824"><a href="dl.php?t=12345">Download</a></td>
                    <td>10</td>
                    <td>5</td>
                    <td>100</td>
                    <td data-ts_text="1609459200">01-01-2021 00:00:00</td>
                </tr>
            </tbody>
        </table>
    </body>
    </html>
    """


@pytest.fixture
def mock_html_search_form():
    """Фикстура с примером HTML формы поиска."""
    return """
    <html>
    <body>
        <form>
            <select id="fs-main" name="f[]">
                <optgroup label="Фильмы">
                    <option value="1" class="root_forum">Фильмы HD</option>
                    <option value="2" class="fp-1 has_sf">Фильмы SD</option>
                </optgroup>
                <optgroup label="Сериалы">
                    <option value="3" class="root_forum">Сериалы HD</option>
                </optgroup>
            </select>
            <select name="o">
                <option value="1" selected>По дате</option>
                <option value="2">По размеру</option>
            </select>
            <input type="radio" name="s" value="1" checked>
            <label>По возрастанию</label>
            <input type="radio" name="s" value="2">
            <label>По убыванию</label>
            <select name="tm">
                <option value="0" selected>За все время</option>
                <option value="1">За последний день</option>
            </select>
        </form>
    </body>
    </html>
    """


@pytest.fixture
def temp_dir():
    """Фикстура для временной директории."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_requests_session():
    """Фикстура для мокирования requests.Session."""
    session = Mock()
    session.cookies = {}
    session.proxies = {}
    return session


@pytest.fixture
def mock_aiohttp_session():
    """Фикстура для мокирования aiohttp.ClientSession."""
    session = Mock()
    session.closed = False
    session.cookie_jar = Mock()
    return session


@pytest.fixture
def sample_search_result_dict():
    """Фикстура с примером словаря результата поиска."""
    return {
        "topic_id": 12345,
        "approved": "проверено",
        "category": "Фильмы",
        "category_url": "https://rutracker.org/forum/viewforum.php?f=123",
        "title": "Test Movie",
        "title_url": "https://rutracker.org/forum/viewtopic.php?t=12345",
        "author": "Author",
        "author_url": "https://rutracker.org/forum/profile.php?u=1",
        "size": 1.0,
        "unit": "GB",
        "download_url": "https://rutracker.org/forum/dl.php?t=12345",
        "seedmed": 10,
        "leechmed": 5,
        "download_counter": 100,
        "added": "01-01-2021 00:00:00"
    }

