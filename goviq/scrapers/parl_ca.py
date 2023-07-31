import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging
import json
import requests
from typing import Iterable, List

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

    def __init__(self, local_cache: str = None):
        self.local_cache = local_cache if local_cache else LOCAL_CACHE
        self.bill_links = self.fetch_bills()

    def fetch_bills(self) -> Iterable[str]:  # TODO: Unit test to make sure this page structure doesnt change.
        """
        Fetches links to bills from parl.ca. Federal level Canadian bills.
        :return: list of bill links
        """
        text = requests.get(self.BILL_URL).text
        soup = BeautifulSoup(text, 'html.parser')
        links = set(soup.find_all('a', class_='bill-tile-popup interactive-popup'))
        return [self.ROOT_URL + link['href'] for link in links]

    async def _parse(self, text):
        """Parses bill text"""
        soup = BeautifulSoup(text, 'html.parser')
        links = soup.find_all('a', class_='publication btn btn-primary')
        links = [link['href'] for link in links if link['href'].startswith('/DocumentViewer/en')]
        # Assert that there is only one link, and then make a request to that link and pull the entire HTML body
        if len(links) != 1:
            raise ValueError(f"Expected 1 link, got {len(links)}")
        link = links[0]
        async with aiohttp.ClientSession() as session:
            html = await self._fetch(self.ROOT_URL + link, session)
        return html

    def _cache(self, links: List[dict], filename='bill_text') -> None:
        """
        Caches the list of links to a file.
        :param links: list of links
        :param filename: filename to cache to
        :return:
        """
        filepath = f"{self.local_cache}/{filename}_{datestamp()}"
        with open(f'{filepath}.json', 'w') as f:
            json.dump(links, f)
        logging.info(f'Cached {len(links)} links to {filepath}.json')

    def crawl(self, local_cache: str = None) -> None:
        loop = asyncio.get_event_loop()
        logging.info('Beginning crawl of parl.ca')
        links = loop.run_until_complete(self._crawl(links=self.bill_links))
        logging.info('Completed crawl of parl.ca. Caching results to disk.')
        self._cache(links)

def main():
    crawler = BillCrawler()
    crawler.crawl()


if __name__ == '__main__':
    main()
