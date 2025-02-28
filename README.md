# Goviq

**Version**: 0.1.0  
**Author**: Julian Whiting (<j2whitin@gmail.com>)

## Overview

**Goviq** is an application for scraping Canadian Govt documents. Created with downstream RAG pipelines in mind.

## Features

- **Asynchronous Crawling**: Uses [`aiohttp`](https://github.com/aio-libs/aiohttp) for efficient, non-blocking I/O.  
- **HTML Parsing**: Leverages [`BeautifulSoup4`](https://www.crummy.com/software/BeautifulSoup/) for HTML content extraction.  
- **Configurable**: Define your own crawler subclasses to handle specific sources or data formats.  
- **Local Caching**: Store the fetched or parsed data to JSON files for offline analysis.

## Installation

1. Clone this repository (or download the source).  
2. Make sure you have a modern version of `pip` and `setuptools`:
   ```bash
   pip install --upgrade pip setuptools
   ```
3. Install **Goviq**. If you have a `pyproject.toml`, you can do:
   ```bash
   pip install .
   ```
   or, if you prefer the “development/editable” mode:
   ```bash
   pip install -e .
   ```

## Building the Dataset

After installing, the primary way to build the dataset is by running:

```bash
python goviq/crawler_poc.py --output_dir .
```

- **`goviq/crawler_poc.py`** is a script that orchestrates the various crawlers to fetch, parse, and save the data.  
- **`--output_dir .`** tells the script to store the resulting data in the current directory.  
- You can change the output directory path as needed.

## Usage (Alternative Methods)

If you want to call individual crawlers rather than the main script:

```bash
python -m goviq.scrapers.parl_ca
```
Or programmatically in Python:

```python
from goviq.scrapers.parl_ca import BillCrawler

crawler = BillCrawler()
crawler.crawl()
```

## TODO:

- Parliament sessions are hardcoded somewhere. Ought to be able to accept a date range or list of sessions to parse
- How to handle different versions of acts?
- I don't know if the local cache env var is still needed. I took a long break from developing this :)
- Update README.md with some info about runtime, dataset size, provenance, etc..  

## Contributing

1. Fork this repository.  
2. Create a feature branch (`git checkout -b feature/my-new-feature`).  
3. Commit your changes (`git commit -am 'Add new feature'`).  
4. Push to your branch (`git push origin feature/my-new-feature`).  
5. Create a pull request.
