# API Documentation

Complete documentation for using the Py_RuTracker library.

## Table of Contents

- [RuTrackerClient (Synchronous Client)](#rutrackerclient-synchronous-client)
  - [Initialization](#initialization)
  - [Search](#search)
  - [Working with Torrents](#working-with-torrents)
  - [Search Form](#search-form)
  - [Authentication](#authentication)
  - [Context Manager](#context-manager)
- [AsyncRuTrackerClient (Asynchronous Client)](#asyncrutrackerclient-asynchronous-client)
  - [Initialization](#initialization-1)
  - [Search](#search-1)
  - [Working with Torrents](#working-with-torrents-1)
  - [Search Form](#search-form-1)
  - [Authentication](#authentication-1)
  - [Session Management](#session-management)
  - [Context Manager](#context-manager-1)
- [Data Models](#data-models)
  - [SearchResult](#searchresult)
  - [SearchFormData](#searchformdata)
- [Exceptions](#exceptions)

---

## RuTrackerClient (Synchronous Client)

### Initialization

#### `__init__(login: str, password: str, proxies: Optional[dict] = None)`

Initializes the synchronous RuTracker client and performs authentication.

**Parameters:**
- `login` (str): Login for authentication.
- `password` (str): Password for authentication.
- `proxies` (Optional[dict]): Optional dictionary with proxy servers for HTTP and HTTPS.

**Example:**
```python
from py_rutracker import RuTrackerClient

# Without proxy
client = RuTrackerClient("your_login", "your_password")

# With proxy
proxies = {
    'http': 'http://proxy:8080',
    'https': 'http://proxy:8080'
}
client = RuTrackerClient("your_login", "your_password", proxies)
```

**Exceptions:**
- `RuTrackerAuthError`: If authentication failed or captcha detected.

---

### Search

#### `search(title: str, page: int = 1, return_search_dict: bool = False) -> list[SearchResult | dict]`

Performs a search by the given title and returns results.

**Parameters:**
- `title` (str): Title to search for.
- `page` (int): Page number for search (default is 1).
- `return_search_dict` (bool): Flag indicating whether to return results as dictionaries (if `True`) or `SearchResult` objects (if `False`).

**Returns:**
- `list[SearchResult | dict]`: List of search results.

**Exceptions:**
- `RuTrackerRequestError`: If an error occurs while executing the request.
- `RuTrackerParsingError`: If an error occurs while parsing search results.

**Example:**
```python
# Get results as SearchResult objects
results = client.search("Static-X", page=1)

# Get results as dictionaries
results_dict = client.search("Static-X", page=1, return_search_dict=True)

for result in results:
    print(f"{result.title} - {result.size} {result.unit}")
```

#### `search_all_pages(title: str, return_search_dict: bool = False, max_pages: Optional[int] = None) -> list[SearchResult | dict]`

Performs a search by the given title on all pages.

**Parameters:**
- `title` (str): Title to search for.
- `return_search_dict` (bool): Flag indicating whether to return results as dictionaries (if `True`) or `SearchResult` objects (if `False`).
- `max_pages` (Optional[int]): Maximum number of pages to search (default is 10). If `None`, the value from constants is used.

**Returns:**
- `list[SearchResult | dict]`: List of all search results from all pages.

**Exceptions:**
- `RuTrackerParsingError`: If an error occurs while parsing search results.

**Example:**
```python
# Search on all pages (up to 10 pages by default)
all_results = client.search_all_pages("Static-X")

# Search with page limit
limited_results = client.search_all_pages("Static-X", max_pages=5)

print(f"Found results: {len(all_results)}")
```

---

### Working with Torrents

#### `get_torrent(topic_id_or_url: int | str) -> bytes`

Gets the torrent file content by the specified identifier or URL.

**Parameters:**
- `topic_id_or_url` (int | str): Topic identifier (int) or URL to get the torrent file (str).

**Returns:**
- `bytes`: Torrent file content as bytes.

**Exceptions:**
- `RuTrackerRequestError`: If the request to get the torrent file ended with an error.
- `RuTrackerDownloadError`: If an invalid parameter was passed or the file was not found.

**Example:**
```python
# By ID
torrent_bytes = client.get_torrent(12345)

# By URL
torrent_bytes = client.get_torrent("https://rutracker.org/forum/dl.php?t=12345")

# Manual saving
with open("torrent.torrent", "wb") as f:
    f.write(torrent_bytes)
```

#### `download(topic_id_or_url: int | str, save_path: Optional[str] = None, filename: Optional[str] = None) -> str`

Downloads the torrent file and saves it to disk.

**Parameters:**
- `topic_id_or_url` (int | str): Topic identifier (int) or URL to get the torrent file (str).
- `save_path` (Optional[str]): Path to the directory for saving the file. If `None`, the current directory is used.
- `filename` (Optional[str]): File name. If `None`, `{topic_id}.torrent` is used.

**Returns:**
- `str`: Full path to the saved file.

**Exceptions:**
- `RuTrackerRequestError`: If the request to get the torrent file ended with an error.
- `RuTrackerDownloadError`: If an invalid parameter was passed or the file was not found.

**Example:**
```python
# Automatic saving with default name
file_path = client.download(12345, save_path="./torrents")
print(f"Torrent saved: {file_path}")

# With specified filename
file_path = client.download(12345, save_path="./torrents", filename="my_torrent")
```

---

### Search Form

#### `get_search_form(force_refresh: bool = False) -> SearchFormData`

Gets RuTracker search form data (forum sections, sort options, time filters).  
Data is cached for 24 hours to reduce the number of requests to the server.

**Parameters:**
- `force_refresh` (bool): Force cache refresh, ignoring TTL (default is `False`).

**Returns:**
- `SearchFormData`: Object with search form data, containing:
  - `forum_groups`: List of forum section groups (`ForumGroup`)
  - `sort_options`: List of sort options (`SortOption`)
  - `sort_directions`: List of sort directions (`SortDirection`)
  - `time_filter_options`: List of time filter options (`TimeFilterOption`)
  - `forum_field_name`: Form field name for forum sections

**Exceptions:**
- `RuTrackerRequestError`: If the request to get the form ended with an error.
- `RuTrackerParsingError`: If an error occurred while parsing the form.

**Example:**
```python
# Get search form (from cache if available)
form_data = client.get_search_form()

# View forum groups
for group in form_data.forum_groups:
    print(f"{group.name}: {len(group.sections)} sections")
    for section in group.sections:
        print(f"  - {section.name} (ID: {section.id})")

# View sort options
for option in form_data.sort_options:
    print(f"{option.value}: {option.name}")

# Force cache refresh
form_data = client.get_search_form(force_refresh=True)
```

---

### Authentication

#### `auth(login: str, password: str) -> None`

Authenticates the user on the RuTracker site. Usually called automatically when initializing the client.

**Parameters:**
- `login` (str): Login for authentication.
- `password` (str): Password for authentication.

**Exceptions:**
- `RuTrackerAuthError`: If the response status code is not 200, authentication failed, or captcha detected.

**Example:**
```python
# Usually not required to call manually
client.auth("your_login", "your_password")
```

---

### Context Manager

The `RuTrackerClient` class supports use as a context manager for automatic session closure:

```python
with RuTrackerClient("login", "password") as client:
    results = client.search("query")
    # Session will automatically close after exiting the block
```

---

## AsyncRuTrackerClient (Asynchronous Client)

### Initialization

#### `__init__(login: str, password: str, proxy: Optional[str] = None, user_agent: Optional[str] = None)`

Initializes the asynchronous RuTracker client.

**Parameters:**
- `login` (str): Login for authentication.
- `password` (str): Password for authentication.
- `proxy` (Optional[str]): Optional proxy server URL (e.g., `'http://proxy:8080'`).
- `user_agent` (Optional[str]): Optional User-Agent for HTTP requests.

**Example:**
```python
from py_rutracker import AsyncRuTrackerClient

client = AsyncRuTrackerClient("your_login", "your_password", proxy="http://proxy:8080")
```

#### `async init() -> aiohttp.ClientSession`

Initializes the asynchronous session and performs authentication.

**Returns:**
- `aiohttp.ClientSession`: aiohttp session object.

**Note:** This method must be called before using the client if a context manager is not used.

**Example:**
```python
client = AsyncRuTrackerClient("login", "password")
await client.init()
# Now you can use the client
results = await client.search("query")
```

---

### Search

#### `async search(title: str, page: int = 1, return_search_dict: bool = False) -> list[SearchResult | dict]`

Asynchronously performs a search by the given title and returns results.

**Parameters:**
- `title` (str): Title to search for.
- `page` (int): Page number for search (default is 1).
- `return_search_dict` (bool): Flag indicating whether to return results as dictionaries (if `True`) or `SearchResult` objects (if `False`).

**Returns:**
- `list[SearchResult | dict]`: List of search results.

**Exceptions:**
- `RuTrackerRequestError`: If an error occurs while executing the request.
- `RuTrackerParsingError`: If an error occurs while parsing search results.

**Example:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    results = await client.search("Static-X", page=1)
    for result in results:
        print(f"{result.title} - {result.size} {result.unit}")
```

#### `async search_all_pages(title: str, return_search_dict: bool = False, max_pages: Optional[int] = None) -> list[SearchResult | dict]`

Asynchronously performs a search by the given title on all pages. Requests to different pages are executed in parallel.

**Parameters:**
- `title` (str): Title to search for.
- `return_search_dict` (bool): Flag indicating whether to return results as dictionaries (if `True`) or `SearchResult` objects (if `False`).
- `max_pages` (Optional[int]): Maximum number of pages to search (default is 10). If `None`, the value from constants is used.

**Returns:**
- `list[SearchResult | dict]`: List of all search results from all pages.

**Exceptions:**
- `RuTrackerParsingError`: If an error occurs while parsing search results.

**Example:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    # Parallel search on all pages
    all_results = await client.search_all_pages("Static-X", max_pages=5)
    print(f"Found results: {len(all_results)}")
```

---

### Working with Torrents

#### `async get_torrent(topic_id_or_url: int | str) -> bytes`

Asynchronously gets the torrent file content by the specified identifier or URL.

**Parameters:**
- `topic_id_or_url` (int | str): Topic identifier (int) or URL to get the torrent file (str).

**Returns:**
- `bytes`: Torrent file content as bytes.

**Exceptions:**
- `RuTrackerRequestError`: If the request to get the torrent file ended with an error.
- `RuTrackerDownloadError`: If an invalid parameter was passed or the file was not found.

**Example:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    torrent_bytes = await client.get_torrent(12345)
    with open("torrent.torrent", "wb") as f:
        f.write(torrent_bytes)
```

#### `async download(topic_id_or_url: int | str, save_path: Optional[str] = None, filename: Optional[str] = None) -> str`

Asynchronously downloads the torrent file and saves it to disk.

**Parameters:**
- `topic_id_or_url` (int | str): Topic identifier (int) or URL to get the torrent file (str).
- `save_path` (Optional[str]): Path to the directory for saving the file. If `None`, the current directory is used.
- `filename` (Optional[str]): File name. If `None`, `{topic_id}.torrent` is used.

**Returns:**
- `str`: Full path to the saved file.

**Exceptions:**
- `RuTrackerRequestError`: If the request to get the torrent file ended with an error.
- `RuTrackerDownloadError`: If an invalid parameter was passed or the file was not found.

**Example:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    results = await client.search("Static-X")
    if results:
        file_path = await client.download(
            results[0].topic_id,
            save_path="./torrents",
            filename=f"{results[0].title[:50]}.torrent"
        )
        print(f"Torrent saved: {file_path}")
```

---

### Search Form

#### `async get_search_form(force_refresh: bool = False) -> SearchFormData`

Asynchronously gets RuTracker search form data (forum sections, sort options, time filters).  
Data is cached for 24 hours to reduce the number of requests to the server.

**Parameters:**
- `force_refresh` (bool): Force cache refresh, ignoring TTL (default is `False`).

**Returns:**
- `SearchFormData`: Object with search form data.

**Exceptions:**
- `RuTrackerRequestError`: If the request to get the form ended with an error or session is not initialized.
- `RuTrackerParsingError`: If an error occurred while parsing the form.

**Example:**
```python
async with AsyncRuTrackerClient("login", "password") as client:
    form_data = await client.get_search_form()
    
    # View forum groups
    for group in form_data.forum_groups:
        print(f"{group.name}: {len(group.sections)} sections")
    
    # Force refresh
    form_data = await client.get_search_form(force_refresh=True)
```

---

### Authentication

#### `async auth() -> None`

Asynchronously authenticates the user on the RuTracker site. Usually called automatically when initializing the session.

**Exceptions:**
- `RuTrackerAuthError`: If the response status code is not 200, authentication failed, or captcha detected.

**Example:**
```python
client = AsyncRuTrackerClient("login", "password")
await client.init()  # auth is called automatically
```

---

### Session Management

#### `async close() -> None`

Closes the asynchronous session. Called automatically when using a context manager.

**Example:**
```python
client = AsyncRuTrackerClient("login", "password")
await client.init()
# ... using the client ...
await client.close()  # Close session manually
```

---

### Context Manager

The `AsyncRuTrackerClient` class supports use as an asynchronous context manager:

```python
async with AsyncRuTrackerClient("login", "password") as client:
    results = await client.search("query")
    # Session will automatically close after exiting the block
```

---

## Data Models

### SearchResult

Search result model containing the following information:

| Field | Type | Description |
|-------|------|-------------|
| `topic_id` | `int` | Topic identifier |
| `approved` | `str` | Result verification status |
| `category` | `str` | Category where the result is placed |
| `category_url` | `Optional[str]` | Category URL |
| `title` | `str` | Result title |
| `title_url` | `Optional[str]` | Result page URL |
| `author` | `str` | Result author |
| `author_url` | `Optional[str]` | Author page URL |
| `size` | `float` | File size |
| `unit` | `str` | File size unit ('bytes', 'KB', 'MB', 'GB') |
| `download_url` | `str` | File download URL |
| `seedmed` | `int` | Number of seeders |
| `leechmed` | `int` | Number of leechers |
| `download_counter` | `int` | Download counter |
| `added` | `str` | Date and time when the result was added |

**Example:**
```python
result = SearchResult(
    topic_id=12345,
    approved="verified",
    category="Movies",
    title="Test Movie",
    author="Author",
    size=1.5,
    unit="GB",
    download_url="https://rutracker.org/forum/dl.php?t=12345",
    seedmed=10,
    leechmed=5,
    download_counter=100,
    added="01-01-2021 00:00:00"
)

print(result.title)  # "Test Movie"
print(f"{result.size} {result.unit}")  # "1.5 GB"
```

### SearchFormData

Search form data model containing:

| Field | Type | Description |
|-------|------|-------------|
| `forum_groups` | `List[ForumGroup]` | List of forum section groups |
| `sort_options` | `List[SortOption]` | List of sort options |
| `sort_directions` | `List[SortDirection]` | List of sort directions |
| `time_filter_options` | `List[TimeFilterOption]` | List of time filter options |
| `forum_field_name` | `str` | Form field name for forum sections |

#### ForumGroup

Forum section group:

| Field | Type | Description |
|-------|------|-------------|
| `name` | `str` | Group name |
| `sections` | `List[ForumSection]` | List of sections in the group |

#### ForumSection

Forum section:

| Field | Type | Description |
|-------|------|-------------|
| `id` | `int` | Section identifier |
| `name` | `str` | Section name |
| `parent_id` | `Optional[int]` | Parent section ID |
| `is_root` | `bool` | Whether the section is root |
| `has_subforums` | `bool` | Whether the section has subforums |

#### SortOption

Sort option:

| Field | Type | Description |
|-------|------|-------------|
| `value` | `int` | Sort option value |
| `name` | `str` | Sort option name |
| `form_field_name` | `str` | Form field name for POST request |
| `is_selected` | `bool` | Whether the option is selected by default |

#### SortDirection

Sort direction:

| Field | Type | Description |
|-------|------|-------------|
| `value` | `int` | Direction value (1 - ascending, 2 - descending) |
| `name` | `str` | Sort direction name |
| `form_field_name` | `str` | Form field name for POST request |
| `is_selected` | `bool` | Whether the direction is selected by default |

#### TimeFilterOption

Time filter option:

| Field | Type | Description |
|-------|------|-------------|
| `value` | `int` | Time filter value |
| `name` | `str` | Time filter name |
| `form_field_name` | `str` | Form field name for POST request |
| `is_selected` | `bool` | Whether the option is selected by default |

---

## Exceptions

The library uses the following exception hierarchy:

### RuTrackerException

Base exception for all library errors. All other exceptions inherit from it.

### RuTrackerAuthError

Authentication errors.

**Possible causes:**
- Invalid login or password
- Captcha detected
- Missing cookies after authentication
- Error executing authentication request

**Example:**
```python
from py_rutracker import RuTrackerClient
from py_rutracker.exceptions import RuTrackerAuthError

try:
    client = RuTrackerClient("wrong_login", "wrong_password")
except RuTrackerAuthError as e:
    print(f"Authentication error: {e}")
```

### RuTrackerRequestError

HTTP request errors.

**Possible causes:**
- Unexpected response status code (not 200)
- Re-authentication required
- Network error when executing request
- Session not initialized (for asynchronous client)

**Example:**
```python
from py_rutracker.exceptions import RuTrackerRequestError

try:
    results = client.search("query")
except RuTrackerRequestError as e:
    print(f"Request error: {e}")
```

### RuTrackerParsingError

HTML parsing errors.

**Possible causes:**
- HTML structure changes on RuTracker site
- Invalid HTML in server response
- Error extracting data from HTML

**Example:**
```python
from py_rutracker.exceptions import RuTrackerParsingError

try:
    results = client.search("query")
except RuTrackerParsingError as e:
    print(f"Parsing error: {e}")
```

### RuTrackerDownloadError

Torrent file download errors.

**Possible causes:**
- Invalid parameter passed (not int and not valid URL)
- File with specified ID not found
- Missing Content-Disposition header in response

**Example:**
```python
from py_rutracker.exceptions import RuTrackerDownloadError

try:
    torrent = client.get_torrent("invalid_id")
except RuTrackerDownloadError as e:
    print(f"Download error: {e}")
```

---

## Additional Information

### Search Form Caching

Search form data is automatically cached for 24 hours. This allows reducing the number of requests to the server and speeding up application operation.

To force cache refresh, use the `force_refresh=True` parameter:

```python
# Force cache refresh
form_data = client.get_search_form(force_refresh=True)
```

### Error Handling

It is recommended to always handle exceptions when working with the library:

```python
from py_rutracker import RuTrackerClient
from py_rutracker.exceptions import (
    RuTrackerAuthError,
    RuTrackerRequestError,
    RuTrackerParsingError,
    RuTrackerDownloadError
)

try:
    client = RuTrackerClient("login", "password")
    results = client.search("query")
    if results:
        client.download(results[0].topic_id)
except RuTrackerAuthError:
    print("Authentication error")
except RuTrackerRequestError:
    print("Request error")
except RuTrackerParsingError:
    print("Parsing error")
except RuTrackerDownloadError:
    print("Download error")
```

