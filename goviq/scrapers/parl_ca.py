import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
import json
import requests
from typing import Iterable, List, Dict, Any

from goviq.config.local_cache import LOCAL_CACHE
from goviq.entities.crawler import Crawler
from goviq.utils import datestamp

logging.getLogger().setLevel(logging.INFO)

class BillCrawler(Crawler):
    """
    Fetches links to bills from parl.ca. Federal level Canadian bills.
    """
    ROOT_URL = "https://www.parl.ca"
    BILL_URL = "https://www.parl.ca/legisinfo/en/legislation-at-a-glance"
    _version = 1

    def __init__(self, local_cache: str = None, max_concurrent_tasks: int = 100):
        super().__init__(max_concurrent_tasks)
        self.local_cache = local_cache if local_cache else LOCAL_CACHE
        self.bill_links = self.fetch_bills()

    def fetch_bills(self) -> Iterable[str]:
        """
        Fetches links to bills from parl.ca. Federal level Canadian bills.
        :return: list of bill links
        """
        try:
            response = requests.get(self.BILL_URL, headers={'User-Agent': self.user_agent})
            response.raise_for_status()
            text = response.text
            soup = BeautifulSoup(text, 'html.parser')
            links = set(soup.find_all('a', class_='bill-tile-popup interactive-popup'))
            return [self.ROOT_URL + link['href'] for link in links if 'href' in link.attrs]
        except requests.RequestException as e:
            logging.error(f"Error fetching bill links: {e}")
            return []

    async def _parse(self, html: str) -> str:
        """
        Asynchronously parses bill HTML content to extract detailed information.
        
        :param html: The HTML content of the bill page.
        :return: The detailed bill HTML content or None.
        """
        if html is None:
            return None
        try:
            soup = BeautifulSoup(html, 'html.parser')
            links = soup.find_all('a', class_='publication btn btn-primary')
            links = [link['href'] for link in links if link.get('href', '').startswith('/DocumentViewer/en')]
            # Assert that there is only one link, and then make a request to that link and pull the entire HTML body
            if len(links) != 1:
                raise ValueError(f"Expected 1 link, got {len(links)}")
            link = links[0]
            detailed_url = self.ROOT_URL + link
            async with aiohttp.ClientSession() as session:
                detailed_html = await self._fetch(detailed_url, session)
            return detailed_html
        except Exception as e:
            logging.error(f"Error parsing HTML: {e}")
            return None

    def _cache(self, data: List[Dict[str, Any]], filename: str = 'bill_text') -> None:
        """
        Caches the list of bill details to a JSON file.

        :param data: List of dictionaries containing bill details.
        :param filename: Base filename to cache to.
        """
        try:
            filepath = f"{self.local_cache}/{filename}_{datestamp()}.json"
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            logging.info(f'Cached {len(data)} bill details to {filepath}')
        except IOError as e:
            logging.error(f"Error writing to cache file {filepath}: {e}")

    def crawl(self, local_cache: str = None) -> None:
        """
        Initiates the crawling process to fetch and cache bill details.
        """
        loop = asyncio.get_event_loop()
        logging.info('Beginning crawl of parl.ca')
        try:
            links = loop.run_until_complete(self._crawl(links=self.bill_links))
            logging.info('Completed crawl of parl.ca. Caching results to disk.')
            self._cache(links)
        except Exception as e:
            logging.error(f"Error during crawl: {e}")
