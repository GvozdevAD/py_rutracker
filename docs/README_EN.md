# Py_RuTracker

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

[Русский](../README.md) | **English**

Py_RuTracker is a Python library for working with RuTracker, a popular Russian torrent tracker. The library provides a convenient and easy-to-use API for searching torrents, retrieving torrent information, and downloading them.

## Key Features

- 🔍 **Torrent Search** — search by name with pagination and filtering support
- ⬇️ **Torrent Download** — automatic `.torrent` file saving or byte retrieval for processing
- 📋 **Search Form** — retrieve forum sections, sorting options, and time filters
- ⚡ **Synchronous and Asynchronous API** — choose the right option for your project
- 🚀 **Performance** — asynchronous client executes requests in parallel for maximum speed
- 💾 **Caching** — automatic caching of search form data to reduce server load
- 📝 **Logging** — configurable logging for debugging and monitoring
- 🛡️ **Error Handling** — detailed exceptions for all error types
- 🔐 **Proxy Support** — work through proxy servers

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Key Features](#key-features)
- [Documentation](#documentation)
- [Examples](#examples)
- [Logging](#logging)
- [Technologies](#technologies)
- [Contributing](#contributing)
- [Notes](#notes)

## Installation

You can install the library in several ways.

### Installation from PyPI

To install the library, use `pip`:

```sh
pip install py-rutracker-client
```

### Installation from Source

#### Option 1: Using Poetry (Recommended)

The project uses Poetry for dependency management. After cloning the repository:

1. Clone the repository:
    ```sh
    git clone https://github.com/GvozdevAD/py_rutracker
    cd py_rutracker
    ```

2. Install dependencies using Poetry:
    ```sh
    poetry install --no-root
    ```

3. Activate the Poetry virtual environment:
    ```sh
    poetry shell
    ```

#### Option 2: Using venv and pip

1. Clone the repository:
    ```sh
    git clone https://github.com/GvozdevAD/py_rutracker
    cd py_rutracker
    ```

2. Create a virtual environment using `venv`:
    ```sh
    python -m venv env
    ```

3. Activate the virtual environment:
    * On Windows:
        ```sh
        env\Scripts\activate
        ```
    * On macOS and Linux:
        ```sh
        source env/bin/activate
        ```

4. Install dependencies from `requirements.txt`:
    ```sh
    pip install -r requirements.txt
    ```

## Quick Start

### Synchronous Client

```python
from py_rutracker import RuTrackerClient

# Create client
client = RuTrackerClient("your_login", "your_password")

# Search torrents
results = client.search_all_pages("Static-X")

# Display results
for torrent in results:
    print(torrent)

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
        results = await client.search_all_pages("rammstein")
        if results:
            file_path = await client.download(
                results[0].topic_id,
                save_path="./torrents"
            )
            print(f"Torrent saved: {file_path}")

asyncio.run(main())
```

## Logging

The library uses centralized logging. By default, only messages at the **WARNING** level and above are logged to avoid cluttering the output. For debugging, you can enable more detailed logging.

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

```bash
export PY_RUTRACKER_LOG_LEVEL=DEBUG
```

Or on Windows:

```cmd
set PY_RUTRACKER_LOG_LEVEL=DEBUG
```

Available levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

### What is Logged

- **DEBUG**: Detailed information about all operations (HTTP requests, search parameters, session closure)
- **INFO**: Successful operations (client initialization, authentication, search results, torrent downloads)
- **WARNING**: Warnings (unexpected status codes, errors on individual pages)
- **ERROR**: Errors (authentication errors, parsing errors, file download errors)

## Technologies

The library uses modern technologies and best practices:

- **Pydantic** — for data validation and models. All data models (`SearchResult`) use Pydantic for automatic type and value validation.
- **aiohttp** — for asynchronous HTTP requests
- **requests** — for synchronous HTTP requests
- **BeautifulSoup4** — for HTML parsing
- **Centralized logging** — for convenient debugging and monitoring

### Benefits of Using Pydantic

- Automatic data type validation
- Type conversion (e.g., strings to numbers)
- Value validation (range checks, format checks)
- Convenient JSON serialization
- Detailed error messages during validation

## Documentation

Full API documentation is available in [DOCUMENTATION_EN.md](DOCUMENTATION_EN.md) (in English) or [DOCUMENTATION.md](DOCUMENTATION.md) (на русском).

The documentation includes:
- Detailed description of all `RuTrackerClient` and `AsyncRuTrackerClient` methods
- Description of data models (`SearchResult`, `SearchFormData`, etc.)
- Description of exceptions and their handling
- Additional information about caching and library operation

## Examples

Detailed usage examples are available in [EXAMPLES_EN.md](EXAMPLES_EN.md) (in English) or [EXAMPLES.md](EXAMPLES.md) (на русском).

The `examples/` folder contains ready-to-use code examples:

- **`basic_usage.py`** — basic usage of the synchronous client
- **`async_usage.py`** — example of using the asynchronous client
- **`get_search_form.py`** — working with the search form (synchronous client)
- **`get_search_form_async.py`** — working with the search form (asynchronous client)
- **`logging_example.py`** — logging configuration examples

You can run any example:

```bash
# Set environment variables before running
export LOGIN="your_login"
export PASSWORD="your_password"
export PROXY="http://proxy:8080"  # Optional

# Run examples
python examples/basic_usage.py
python examples/async_usage.py
python examples/get_search_form.py
python examples/get_search_form_async.py
python examples/logging_example.py
```

## Contributing

Contributions to the project are welcome! If you want to help the project:

1. **Create a separate branch** from `develop`:
   ```bash
   git checkout develop
   git pull origin develop
   git checkout -b feature/your-feature-name
   ```

2. **Make changes** and ensure the code follows the project style

3. **Create a Merge Request (MR)** to the `develop` branch:
   - Make sure your changes don't break existing functionality
   - Add a description of changes in the MR
   - Specify related issues (if any)

4. **Wait for review** — I will review your MR and suggest improvements if necessary

### Project Structure

```
py_rutracker/
├── clients/          # Clients (sync, async)
├── core/             # Core library (base class, constants)
├── models/           # Data models (Pydantic)
├── parsers/          # HTML parsers
├── utils/            # Utilities (validation, helpers)
├── logger.py         # Centralized logging
├── exceptions.py     # Exceptions
└── enums.py          # Enumerations
```

## Notes

* Replace "your_login" and "your_password" with your actual RuTracker credentials.
* Specify a proxy in the dictionary if your request requires using a proxy. If a proxy is not required, you can omit this parameter.
* The library uses an unofficial RuTracker API and may not work if the site changes.

