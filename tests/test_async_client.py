from unittest.mock import AsyncMock, MagicMock, Mock, mock_open, patch

import pytest

from py_rutracker.clients.async_client import AsyncRuTrackerClient
from py_rutracker.exceptions import (RuTrackerAuthError,
                                     RuTrackerDownloadError,
                                     RuTrackerRequestError)


class AsyncContextManagerMock:
    """Mock для async context manager."""
    def __init__(self, mock_response):
        self.mock_response = mock_response
    
    async def __aenter__(self):
        return self.mock_response
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        return None


def create_async_context_manager(mock_response):
    """Создает правильный async context manager mock для aiohttp."""
    return AsyncContextManagerMock(mock_response)


class TestAsyncRuTrackerClient:
    """Тесты для класса AsyncRuTrackerClient."""
    
    def test_init(self):
        """Тест инициализации."""
        client = AsyncRuTrackerClient("test_login", "test_password")
        assert client._login == "test_login"
        assert client._password == "test_password"
        assert client.session is None
        assert client.user_agent is not None
    
    def test_init_with_proxy(self):
        """Тест инициализации с прокси."""
        client = AsyncRuTrackerClient("login", "password", proxy="http://proxy:8080")
        assert client.proxy == "http://proxy:8080"
    
    def test_init_with_user_agent(self):
        """Тест инициализации с User-Agent."""
        custom_ua = "Custom User Agent"
        client = AsyncRuTrackerClient("login", "password", user_agent=custom_ua)
        assert client.user_agent == custom_ua
    
    @pytest.mark.asyncio
    async def test_init_method(self):
        """Тест метода init."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = AsyncMock()
        mock_session.cookie_jar = Mock()
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            with patch.object(client, 'auth', new_callable=AsyncMock):
                session = await client.init()
                assert session == mock_session
    
    @pytest.mark.asyncio
    async def test_auth_success(self):
        """Тест успешной аутентификации."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = MagicMock()
        mock_session.cookie_jar = Mock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="success")
        mock_session.post = MagicMock(return_value=create_async_context_manager(mock_response))
        client.session = mock_session
        
        await client.auth()
        mock_session.post.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_auth_error(self):
        """Тест ошибки аутентификации."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = MagicMock()
        mock_session.cookie_jar = None
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value="success")
        mock_session.post = MagicMock(return_value=create_async_context_manager(mock_response))
        client.session = mock_session
        
        with pytest.raises(RuTrackerAuthError):
            await client.auth()
    
    @pytest.mark.asyncio
    async def test_search(self, mock_html_search_results):
        """Тест поиска."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html_search_results)
        mock_session.get = MagicMock(return_value=create_async_context_manager(mock_response))
        client.session = mock_session
        
        results = await client.search("test query")
        assert len(results) == 1
    
    @pytest.mark.asyncio
    async def test_search_error_status(self):
        """Тест поиска с ошибкой статуса."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.status = 404
        mock_session.get = MagicMock(return_value=create_async_context_manager(mock_response))
        client.session = mock_session
        
        with pytest.raises(RuTrackerRequestError):
            await client.search("test query")
    
    @pytest.mark.asyncio
    async def test_search_all_pages(self, mock_html_search_results):
        """Тест поиска по всем страницам."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html_search_results)
        mock_session.get = MagicMock(return_value=create_async_context_manager(mock_response))
        client.session = mock_session
        
        results = await client.search_all_pages("test query", max_pages=2)
        assert len(results) > 0
    
    @pytest.mark.asyncio
    async def test_get_torrent(self):
        """Тест получения торрента."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Disposition": "filename=test.torrent"}
        mock_response.read = AsyncMock(return_value=b"torrent bytes")
        mock_session.get = MagicMock(return_value=create_async_context_manager(mock_response))
        client.session = mock_session
        
        content = await client.get_torrent(12345)
        assert content == b"torrent bytes"
    
    @pytest.mark.asyncio
    async def test_get_torrent_no_content_disposition(self):
        """Тест получения торрента без Content-Disposition."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {}
        mock_response.read = AsyncMock(return_value=b"torrent bytes")
        mock_session.get = MagicMock(return_value=create_async_context_manager(mock_response))
        client.session = mock_session
        
        with pytest.raises(RuTrackerDownloadError):
            await client.get_torrent(12345)
    
    @pytest.mark.asyncio
    async def test_download(self, temp_dir):
        """Тест скачивания торрента."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = MagicMock()
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.headers = {"Content-Disposition": "filename=test.torrent"}
        mock_response.read = AsyncMock(return_value=b"torrent bytes")
        mock_session.get = MagicMock(return_value=create_async_context_manager(mock_response))
        client.session = mock_session
        
        with patch('builtins.open', mock_open()) as mock_file:
            with patch('py_rutracker.core.base.Path.mkdir'):
                path = await client.download(12345, save_path=str(temp_dir))
                assert path.endswith(".torrent")
                mock_file.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_get_search_form(self, mock_html_search_form):
        """Тест получения формы поиска."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = MagicMock()
        mock_session.closed = False
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.text = AsyncMock(return_value=mock_html_search_form)
        mock_session.get = MagicMock(return_value=create_async_context_manager(mock_response))
        client.session = mock_session
        
        form_data = await client.get_search_form()
        assert form_data is not None
    
    @pytest.mark.asyncio
    async def test_get_search_form_session_not_initialized(self):
        """Тест получения формы поиска без инициализированной сессии."""
        client = AsyncRuTrackerClient("login", "password")
        client.session = None
        
        with pytest.raises(RuTrackerRequestError):
            await client.get_search_form()
    
    @pytest.mark.asyncio
    async def test_get_search_form_session_closed(self):
        """Тест получения формы поиска с закрытой сессией."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = AsyncMock()
        mock_session.closed = True
        client.session = mock_session
        
        with pytest.raises(RuTrackerRequestError):
            await client.get_search_form()
    
    @pytest.mark.asyncio
    async def test_close(self):
        """Тест закрытия сессии."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = AsyncMock()
        mock_session.closed = False
        mock_session.close = AsyncMock()
        client.session = mock_session
        
        await client.close()
        mock_session.close.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_close_already_closed(self):
        """Тест закрытия уже закрытой сессии."""
        client = AsyncRuTrackerClient("login", "password")
        mock_session = AsyncMock()
        mock_session.closed = True
        client.session = mock_session
        
        await client.close()  # Не должно быть ошибки
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Тест асинхронного контекстного менеджера."""
        mock_session = AsyncMock()
        mock_session.cookie_jar = Mock()
        mock_session.closed = False
        mock_session.close = AsyncMock()
        
        with patch('aiohttp.ClientSession', return_value=mock_session):
            with patch.object(AsyncRuTrackerClient, 'auth', new_callable=AsyncMock):
                async with AsyncRuTrackerClient("login", "password") as client:
                    assert client is not None
                
                mock_session.close.assert_called_once()

