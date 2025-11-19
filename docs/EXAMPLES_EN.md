# Usage Examples

Detailed usage examples for the Py_RuTracker library.

## Table of Contents

- [Quick Start](#quick-start)
- [Synchronous Client (RuTrackerClient)](#synchronous-client-rutrackerclient)
  - [Basic Usage](#basic-usage)
  - [Search on One Page](#search-on-one-page)
  - [Search on All Pages](#search-on-all-pages)
  - [Downloading Torrents](#downloading-torrents)
  - [Working with Search Form](#working-with-search-form)
  - [Using Proxy](#using-proxy)
  - [Context Manager](#context-manager)
- [Asynchronous Client (AsyncRuTrackerClient)](#asynchronous-client-asyncrutrackerclient)
  - [Basic Usage](#basic-usage-1)
  - [Parallel Search](#parallel-search)
  - [Downloading Torrents](#downloading-torrents-1)
  - [Working with Search Form](#working-with-search-form-1)
- [Logging](#logging)
- [Error Handling](#error-handling)

---

## Quick Start

### Synchronous Client

```python
from py_rutracker import RuTrackerClient

# Create client
client = RuTrackerClient("your_login", "your_password")

# Search
results = client.search("Static-X")

# Display results
for result in results:
    print(f"{result.title} - {result.size} {result.unit}")

# Download first torrent
if results:
    file_path = client.download(results[0].topic_id, save_path="./torrents")
    print(f"Torrent saved: {file_path}")
```

### Asynchronous Client

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        results = await client.search("Static-X")
        for result in results:
            print(f"{result.title} - {result.size} {result.unit}")
        
        if results:
            file_path = await client.download(
                results[0].topic_id,
                save_path="./torrents"
            )
            print(f"Torrent saved: {file_path}")

asyncio.run(main())
```

---

## Synchronous Client (RuTrackerClient)

### Basic Usage

```python
from py_rutracker import RuTrackerClient

# Create client with credentials
client = RuTrackerClient("your_login", "your_password")

# Search torrents by query
results = client.search_all_pages("Static-X")

# Display information about each torrent
for torrent in results:
    print(torrent)
    print("-" * 50)
```

**Example output:**
```
Topic ID: 65341
Title: (Industrial, Alternative) Static-X - Start A War - 2005, APE (image + .cue), lossless
Author: SLTK
Category: Alternative & Nu-metal (lossless)
Size: 310.41 MB
Download URL: https://rutracker.org/forum/dl.php?t=65341
Added: 27-08-2006 10:53:01
Seed: 10
Leech: 0
Download Counter: 2526
--------------------------------------------------
```

### Search on One Page

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Search on first page
results = client.search("Static-X", page=1)

print(f"Found results on page 1: {len(results)}")

# Search on second page
results_page_2 = client.search("Static-X", page=2)
print(f"Found results on page 2: {len(results_page_2)}")
```

### Search on All Pages

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Search on all pages (up to 10 by default)
all_results = client.search_all_pages("Static-X")
print(f"Total results found: {len(all_results)}")

# Search with page limit
limited_results = client.search_all_pages("Static-X", max_pages=5)
print(f"Found results on 5 pages: {len(limited_results)}")

# Get results as dictionaries
results_dict = client.search_all_pages("Static-X", return_search_dict=True)
for result in results_dict:
    print(result["title"], result["size"], result["unit"])
```

### Downloading Torrents

#### Option 1: Automatic Saving (Recommended)

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")
results = client.search_all_pages("Static-X")

if results:
    topic_id = results[0].topic_id
    
    # Automatically saves file to specified directory
    file_path = client.download(
        topic_id,
        save_path="./torrents",  # Path to folder for saving
        filename=None  # If None, topic_id.torrent is used
    )
    print(f"Torrent saved: {file_path}")
```

#### Option 2: Getting Bytes for Additional Processing

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")
results = client.search_all_pages("Static-X")

if results:
    topic_id = results[0].topic_id
    
    # Get bytes for additional processing
    bytes_data = client.get_torrent(topic_id)
    
    # Can save with custom name
    with open(f"{results[0].title[:50]}.torrent", "wb") as file:
        file.write(bytes_data)
    
    # Or process bytes before saving
    # processed_data = process_torrent(bytes_data)
```

#### Downloading by URL

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Can use URL instead of topic_id
url = "https://rutracker.org/forum/dl.php?t=12345"
file_path = client.download(url, save_path="./torrents")
```

### Working with Search Form

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")

# Get search form (will be cached for 24 hours)
form_data = client.get_search_form()

print(f"Found forum groups: {len(form_data.forum_groups)}")
print(f"Found sort options: {len(form_data.sort_options)}")
print(f"Found sort directions: {len(form_data.sort_directions)}")
print(f"Found time filters: {len(form_data.time_filter_options)}\n")

# View forum groups
print("Forum groups:")
for group in form_data.forum_groups:
    print(f"\n{group.name} ({len(group.sections)} sections)")
    for section in group.sections[:5]:  # First 5 sections
        indent = "  " if section.parent_id else ""
        print(f"{indent}- [{section.id}] {section.name}")
        if section.has_subforums:
            print(f"{indent}  (has subforums)")

# View sort options
print("\n\nSort options:")
for option in form_data.sort_options:
    selected = "✓" if option.is_selected else " "
    print(f"  [{selected}] {option.value}: {option.name}")

# View sort directions
print("\n\nSort directions:")
for direction in form_data.sort_directions:
    selected = "✓" if direction.is_selected else " "
    print(f"  [{selected}] {direction.value}: {direction.name}")

# View time filters
print("\n\nTime filters:")
for time_filter in form_data.time_filter_options:
    selected = "✓" if time_filter.is_selected else " "
    print(f"  [{selected}] {time_filter.value}: {time_filter.name}")

# Second call - data will be taken from cache
print("\n\nSecond call to get_search_form() - data from cache:")
form_data_cached = client.get_search_form()
print(f"Data retrieved from cache: {form_data_cached == form_data}")

# Force cache refresh
print("\n\nForce cache refresh:")
form_data_refreshed = client.get_search_form(force_refresh=True)
print(f"Cache updated, groups received: {len(form_data_refreshed.forum_groups)}")
```

### Using Proxy

```python
from py_rutracker import RuTrackerClient

# Configure proxy
proxies = {
    'http': 'http://proxy.example.com:8080',
    'https': 'http://proxy.example.com:8080'
}

# Create client with proxy
client = RuTrackerClient("your_login", "your_password", proxies=proxies)

# Use client as usual
results = client.search("Static-X")
```

### Context Manager

Using a context manager ensures automatic session closure:

```python
from py_rutracker import RuTrackerClient

# Session will automatically close after exiting the block
with RuTrackerClient("your_login", "your_password") as client:
    results = client.search_all_pages("Static-X")
    for torrent in results:
        print(torrent)
    
    if results:
        client.download(results[0].topic_id, save_path="./torrents")

# Session is already closed here
```

---

## Asynchronous Client (AsyncRuTrackerClient)

### Basic Usage

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        results = await client.search_all_pages("rammstein")
        
        for result in results:
            print(f"{result.title} - {result.size} {result.unit}")
        
        if results:
            file_path = await client.download(
                results[0].topic_id,
                save_path="./torrents",
                filename=f"{results[0].title[:50]}.torrent"
            )
            print(f"Torrent saved: {file_path}")

asyncio.run(main())
```

### Parallel Search

The asynchronous client executes requests to different pages in parallel:

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        # Requests to pages 1-10 are executed in parallel
        all_results = await client.search_all_pages("Static-X", max_pages=10)
        print(f"Found results: {len(all_results)}")

asyncio.run(main())
```

### Downloading Torrents

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        results = await client.search("Static-X")
        
        if results:
            # Option 1: Automatic saving
            file_path = await client.download(
                results[0].topic_id,
                save_path="./torrents",
                filename=f"{results[0].title[:50]}.torrent"
            )
            print(f"Torrent saved: {file_path}")
            
            # Option 2: Getting bytes
            # bytes_data = await client.get_torrent(results[0].topic_id)
            # with open(f"{results[0].topic_id}.torrent", "wb") as file:
            #     file.write(bytes_data)

asyncio.run(main())
```

### Working with Search Form

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        # Get search form (will be cached for 24 hours)
        form_data = await client.get_search_form()
        
        print(f"Found forum groups: {len(form_data.forum_groups)}")
        print(f"Found sort options: {len(form_data.sort_options)}")
        
        # View forum groups
        for group in form_data.forum_groups[:3]:
            print(f"\n{group.name} ({len(group.sections)} sections)")
            for section in group.sections[:3]:
                print(f"  - [{section.id}] {section.name}")
        
        # Second call - data from cache
        form_data_cached = await client.get_search_form()
        print(f"\nData from cache: {form_data_cached == form_data}")
        
        # Force refresh
        form_data_refreshed = await client.get_search_form(force_refresh=True)
        print(f"Cache updated")

asyncio.run(main())
```

### Using Without Context Manager

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient

async def main():
    client = AsyncRuTrackerClient("your_login", "your_password")
    
    try:
        # Initialize session
        await client.init()
        
        # Use client
        results = await client.search("Static-X")
        print(f"Found results: {len(results)}")
        
    finally:
        # Close session
        await client.close()

asyncio.run(main())
```

---

## Logging

### Setting Log Level

#### Option 1: Using the `configure_logger` function

```python
import logging
from py_rutracker import RuTrackerClient, configure_logger

# Set INFO level
configure_logger(level='INFO')

# Or use constants from the logging module
configure_logger(level=logging.DEBUG)

# With file logging
configure_logger(
    level='DEBUG',
    log_to_file=True,
    log_file_path="rutracker.log"
)

client = RuTrackerClient("your_login", "your_password")
```

#### Option 2: Using environment variable

Set the environment variable before running:

**Linux/macOS:**
```bash
export PY_RUTRACKER_LOG_LEVEL=DEBUG
python your_script.py
```

**Windows:**
```cmd
set PY_RUTRACKER_LOG_LEVEL=DEBUG
python your_script.py
```

**Available levels:** `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### What is Logged

- **DEBUG**: Detailed information about all operations (HTTP requests, search parameters, session closure)
- **INFO**: Successful operations (client initialization, authentication, search results, torrent downloads)
- **WARNING**: Warnings (unexpected status codes, errors on individual pages)
- **ERROR**: Errors (authentication errors, parsing errors, file download errors)

### Logging Configuration Example

```python
from py_rutracker import RuTrackerClient, configure_logger

# Configure logging before using client
configure_logger(
    level='DEBUG',
    log_to_file=True,
    log_file_path="rutracker.log",
    format_string='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

client = RuTrackerClient("your_login", "your_password")
results = client.search("Static-X")
```

---

## Error Handling

### Handling All Exception Types

```python
from py_rutracker import RuTrackerClient
from py_rutracker.exceptions import (
    RuTrackerAuthError,
    RuTrackerRequestError,
    RuTrackerParsingError,
    RuTrackerDownloadError
)

try:
    client = RuTrackerClient("your_login", "your_password")
    results = client.search("Static-X")
    
    if results:
        file_path = client.download(results[0].topic_id, save_path="./torrents")
        print(f"Torrent saved: {file_path}")
        
except RuTrackerAuthError as e:
    print(f"Authentication error: {e}")
    # May need to pass captcha in browser
    
except RuTrackerRequestError as e:
    print(f"Request error: {e}")
    # Network or server problem
    
except RuTrackerParsingError as e:
    print(f"Parsing error: {e}")
    # Site structure may have changed
    
except RuTrackerDownloadError as e:
    print(f"Download error: {e}")
    # File not found or invalid parameter
    
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Error Handling When Searching All Pages

```python
from py_rutracker import RuTrackerClient
from py_rutracker.exceptions import RuTrackerParsingError

client = RuTrackerClient("your_login", "your_password")

try:
    # Search on all pages
    # If an error occurs on any page, it will be logged,
    # but search will continue on next pages
    results = client.search_all_pages("Static-X", max_pages=10)
    print(f"Found results: {len(results)}")
    
except RuTrackerParsingError as e:
    print(f"Critical parsing error: {e}")
```

### Checking Results Before Use

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")
results = client.search("Static-X")

# Always check for results
if results:
    first_result = results[0]
    print(f"First result: {first_result.title}")
    
    # Check for topic_id before downloading
    if first_result.topic_id:
        try:
            file_path = client.download(first_result.topic_id, save_path="./torrents")
            print(f"Torrent saved: {file_path}")
        except Exception as e:
            print(f"Failed to download torrent: {e}")
else:
    print("No results found")
```

---

## Additional Examples

### Filtering Results by Size

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")
results = client.search_all_pages("Static-X")

# Filter results larger than 1 GB
large_torrents = [
    r for r in results 
    if r.unit == "GB" and r.size >= 1.0
]

print(f"Found torrents larger than 1 GB: {len(large_torrents)}")
for torrent in large_torrents:
    print(f"{torrent.title} - {torrent.size} {torrent.unit}")
```

### Search with Best Seeder/Leecher Ratio

```python
from py_rutracker import RuTrackerClient

client = RuTrackerClient("your_login", "your_password")
results = client.search("Static-X")

# Sort by number of seeders
sorted_results = sorted(
    results,
    key=lambda x: x.seedmed,
    reverse=True
)

print("Top 5 results by number of seeders:")
for i, result in enumerate(sorted_results[:5], 1):
    print(f"{i}. {result.title}")
    print(f"   Seeders: {result.seedmed}, Leechers: {result.leechmed}")
```

### Bulk Torrent Download

```python
from py_rutracker import RuTrackerClient
from py_rutracker.exceptions import RuTrackerDownloadError

client = RuTrackerClient("your_login", "your_password")
results = client.search_all_pages("Static-X")

# Download first 10 torrents
downloaded = 0
failed = 0

for i, result in enumerate(results[:10], 1):
    try:
        file_path = client.download(
            result.topic_id,
            save_path="./torrents",
            filename=f"{i}_{result.topic_id}.torrent"
        )
        print(f"[{i}/10] Downloaded: {result.title[:50]}")
        downloaded += 1
    except RuTrackerDownloadError as e:
        print(f"[{i}/10] Error: {result.title[:50]} - {e}")
        failed += 1

print(f"\nDownloaded: {downloaded}, Errors: {failed}")
```

### Asynchronous Bulk Download

```python
import asyncio
from py_rutracker import AsyncRuTrackerClient
from py_rutracker.exceptions import RuTrackerDownloadError

async def download_torrent(client, result, index):
    try:
        file_path = await client.download(
            result.topic_id,
            save_path="./torrents",
            filename=f"{index}_{result.topic_id}.torrent"
        )
        print(f"[{index}] Downloaded: {result.title[:50]}")
        return True
    except RuTrackerDownloadError as e:
        print(f"[{index}] Error: {result.title[:50]} - {e}")
        return False

async def main():
    async with AsyncRuTrackerClient("your_login", "your_password") as client:
        results = await client.search_all_pages("Static-X")
        
        # Parallel download of first 10 torrents
        tasks = [
            download_torrent(client, result, i)
            for i, result in enumerate(results[:10], 1)
        ]
        
        results_download = await asyncio.gather(*tasks)
        downloaded = sum(results_download)
        
        print(f"\nDownloaded: {downloaded} out of {len(tasks)}")

asyncio.run(main())
```

---

## Ready Examples

The `examples/` folder contains ready-to-use examples of the library:

- **`basic_usage.py`** — basic usage of the synchronous client
- **`async_usage.py`** — example of using the asynchronous client
- **`get_search_form.py`** — working with the search form (synchronous client)
- **`get_search_form_async.py`** — working with the search form (asynchronous client)
- **`logging_example.py`** — logging configuration examples

You can run any example:

```bash
python examples/basic_usage.py
python examples/async_usage.py
python examples/get_search_form.py
python examples/get_search_form_async.py
python examples/logging_example.py
```

**Note:** Before running examples, set environment variables:
```bash
export LOGIN="your_login"
export PASSWORD="your_password"
export PROXY="http://proxy:8080"  # Optional
```

