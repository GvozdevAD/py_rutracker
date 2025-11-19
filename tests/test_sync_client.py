from unittest.mock import Mock, mock_open, patch

import pytest

from py_rutracker.clients.sync import RuTrackerClient
from py_rutracker.exceptions import (RuTrackerAuthError,
                                     RuTrackerDownloadError,
                                     RuTrackerRequestError)


class TestRuTrackerClient:
    """Тесты для класса RuTrackerClient."""
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_init(self, mock_auth, mock_requests):
        """Тест инициализации клиента."""
        mock_session = Mock()
        mock_requests.session.return_value = mock_session
        client = RuTrackerClient("test_login", "test_password")
        assert client._login == "test_login"
        assert client._password == "test_password"
        mock_auth.assert_called_once()
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_init_with_proxies(self, mock_auth, mock_requests):
        """Тест инициализации с прокси."""
        mock_sess = Mock()
        mock_requests.session.return_value = mock_sess
        proxies = {"http": "http://proxy:8080"}
        client = RuTrackerClient("login", "password", proxies=proxies)
        mock_sess.proxies.update.assert_called_once_with(proxies)
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_send_request_success(self, mock_auth, mock_requests):
        """Тест успешной отправки запроса."""
        mock_sess = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "success"
        mock_sess.get.return_value = mock_response
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        response = client._send_request("http://example.com")
        assert response == mock_response
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_send_request_error_status(self, mock_auth, mock_requests):
        """Тест запроса с ошибкой статуса."""
        mock_sess = Mock()
        mock_response = Mock()
        mock_response.status_code = 404
        mock_sess.get.return_value = mock_response
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        with pytest.raises(RuTrackerRequestError):
            client._send_request("http://example.com")
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_send_request_auth_required(self, mock_auth, mock_requests):
        """Тест запроса требующего аутентификации."""
        mock_sess = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "top-login-box"
        mock_sess.get.return_value = mock_response
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        with pytest.raises(RuTrackerRequestError):
            client._send_request("http://example.com")
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_send_request_exception(self, mock_auth, mock_requests):
        """Тест исключения при запросе с retry механизмом."""
        import requests as requests_module
        mock_sess = Mock()
        mock_sess.get.side_effect = requests_module.exceptions.ConnectionError("Network error")
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        with pytest.raises(RuTrackerRequestError) as exc_info:
            client._send_request("http://example.com")
        assert exc_info.value.url == "http://example.com"
        assert "Network error" in str(exc_info.value)
        assert mock_sess.get.call_count == 3
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_auth_success(self, mock_auth, mock_requests):
        """Тест успешной аутентификации."""
        mock_sess = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "success"
        mock_sess.post.return_value = mock_response
        mock_sess.cookies = {"session": "cookie"}
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        assert mock_auth.called
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_search(self, mock_auth, mock_requests, mock_html_search_results):
        """Тест поиска."""
        mock_sess = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html_search_results
        mock_sess.get.return_value = mock_response
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        results = client.search("test query")
        assert len(results) == 1
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_search_all_pages(self, mock_auth, mock_requests, mock_html_search_results):
        """Тест поиска по всем страницам."""
        mock_sess = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html_search_results
        mock_sess.get.return_value = mock_response
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        results = client.search_all_pages("test query", max_pages=2)
        assert len(results) > 0
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_get_torrent(self, mock_auth, mock_requests):
        """Тест получения торрента."""
        mock_sess = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "torrent content"
        mock_response.content = b"torrent bytes"
        mock_sess.get.return_value = mock_response
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        content = client.get_torrent(12345)
        assert content == b"torrent bytes"
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_get_torrent_error(self, mock_auth, mock_requests):
        """Тест получения торрента с ошибкой."""
        mock_sess = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "Error: File not found"
        mock_response.content = b"error"
        mock_sess.get.return_value = mock_response
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        with pytest.raises(RuTrackerDownloadError):
            client.get_torrent(12345)
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    @patch('builtins.open', new_callable=mock_open)
    @patch('py_rutracker.core.base.Path.mkdir')
    def test_download(self, mock_mkdir, mock_file, mock_auth, mock_requests, temp_dir):
        """Тест скачивания торрента."""
        mock_sess = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = "torrent content"
        mock_response.content = b"torrent bytes"
        mock_sess.get.return_value = mock_response
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        with patch('py_rutracker.core.base.Path.cwd', return_value=temp_dir):
            path = client.download(12345, save_path=str(temp_dir))
            assert path.endswith(".torrent")
            mock_file.assert_called_once()
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_get_search_form(self, mock_auth, mock_requests, mock_html_search_form):
        """Тест получения формы поиска."""
        mock_sess = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html_search_form
        mock_sess.get.return_value = mock_response
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        form_data = client.get_search_form()
        assert form_data is not None
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_get_search_form_cache(self, mock_auth, mock_requests, mock_html_search_form):
        """Тест получения формы поиска из кеша."""
        mock_sess = Mock()
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = mock_html_search_form
        mock_sess.get.return_value = mock_response
        mock_requests.session.return_value = mock_sess
        
        client = RuTrackerClient("login", "password")
        form_data1 = client.get_search_form()
        form_data2 = client.get_search_form()  # Должен быть из кеша
        assert form_data1 == form_data2
    
    @patch('py_rutracker.clients.sync.requests')
    @patch.object(RuTrackerClient, 'auth')
    def test_context_manager(self, mock_auth, mock_requests):
        """Тест контекстного менеджера."""
        mock_sess = Mock()
        mock_requests.session.return_value = mock_sess
        
        with RuTrackerClient("login", "password") as client:
            assert client is not None
        
        mock_sess.close.assert_called_once()

