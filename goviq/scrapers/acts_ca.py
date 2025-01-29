# act_crawler.py
import asyncio
import logging
import json
from bs4 import BeautifulSoup
import aiohttp

from typing import List, Dict, Any

from goviq.config.local_cache import LOCAL_CACHE
from goviq.entities.crawler import Crawler
from goviq.utils import datestamp

logging.getLogger().setLevel(logging.INFO)

class ActCrawler(Crawler):
    """
    Fetches links to acts from laws.justice.gc.ca. Federal-level Canadian acts.
    """
    ROOT_URL = "https://laws-lois.justice.gc.ca/eng/acts/"
    ALPHABET = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
    ACT_URLS = [f"https://laws-lois.justice.gc.ca/eng/acts/{a}.html" for a in ALPHABET]

    def __init__(self, local_cache: str = None, max_concurrent_tasks: int = 50):
        """
        :param local_cache: Directory path for cached output.
        :param max_concurrent_tasks: How many pages to fetch concurrently.
        """
        super().__init__(max_concurrent_tasks=max_concurrent_tasks)
        self.local_cache = local_cache if local_cache else LOCAL_CACHE

    def _parse_index(self, html: str) -> List[str]:
        """
        Parses the alphabetical index page to find each Act's "FullText.html" link.
        Returns absolute URLs for each Act's full text.
        """
        soup = BeautifulSoup(html, "html.parser")
        link_elements = soup.find_all("a", {"class": "TocTitle"})
        # Convert relative URLs to absolute "FullText.html" links
        fulltext_links = []
        for link in link_elements:
            href = link.get("href", "")
            if href.endswith("index.html"):
                full_url = self.ROOT_URL + href.replace("index.html", "FullText.html")
                fulltext_links.append(full_url)
        return fulltext_links

    async def _parse(self, html: str) -> List[str]:
        """
        Asynchronously parses the final FullText.html page to extract the text of the Act.
        Returns a list of text segments (one per <div class="docContents">).
        """
        if html is None:
            return []
        soup = BeautifulSoup(html, "html.parser")
        div_elements = soup.find_all("div", {"class": "docContents"})
        return [div_element.get_text(strip=True) for div_element in div_elements]

    async def _fetch_act_urls(self) -> List[str]:
        """
        Asynchronously fetches all index pages and compiles a list of final FullText.html links.
        """
        act_urls = []
        connector = aiohttp.TCPConnector(limit=50)
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self._fetch(url, session) for url in self.ACT_URLS]
            # Each item is either the HTML or None
            index_pages = await asyncio.gather(*tasks, return_exceptions=True)

        for idx, result in enumerate(index_pages):
            if isinstance(result, Exception):
                logging.error(f"Index fetch for {self.ACT_URLS[idx]} failed: {result}")
            elif result is not None:
                # Parse the index page to get final act links
                final_links = self._parse_index(result)
                act_urls.extend(final_links)

        return act_urls

    def _cache(self, data: List[Dict[str, Any]], filename: str = "act_text") -> None:
        """
        Caches the results to a JSON file with a datestamp.
        """
        filepath = f"{self.local_cache}/{filename}_{datestamp()}.json"
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            logging.info(f"Cached {len(data)} items to {filepath}")
        except IOError as e:
            logging.error(f"Error writing cache file {filepath}: {e}")

    def crawl(self) -> None:
        """
        Main entry point: fetches index pages, extracts final Act URLs, then crawls them for text.
        """
        logging.info("Fetching Act index pages...")
        loop = asyncio.get_event_loop()
        act_urls = loop.run_until_complete(self._fetch_act_urls())
        logging.info(f"Found {len(act_urls)} final Act links. Beginning crawl...")

        # Now fetch + parse the actual FullText.html pages
        results = loop.run_until_complete(self._crawl(act_urls))

        # results is a list of dicts: [{url: [list_of_text_segments]}, ...]
        self._cache(results)
        logging.info("ActCrawler crawl complete.")
