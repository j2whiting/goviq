import aiohttp
import asyncio
from bs4 import BeautifulSoup
import logging

from goviq.config.local_cache import LOCAL_CACHE
from goviq.entities.crawler import Crawler

logging.getLogger().setLevel(logging.INFO)


class ActCrawler(Crawler):
    """
    Fetches links to acts from laws.justice.gc.ca. Federal level Canadian acts.
    """
    ROOT_URL = "https://laws-lois.justice.gc.ca/eng/acts/"
    alphabet = list('ABCDEFGHIJKLMNOPQRSTUVWXYZ')
    ACT_URLS = [f"https://laws-lois.justice.gc.ca/eng/acts/{a}.html" for a in alphabet]

    _version = 1

    def __init__(self, local_cache: str = None):
        self.local_cache = local_cache if local_cache else LOCAL_CACHE

    def _parse_index(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        div_elements = soup.find_all('a', {'class': 'TocTitle'})
        return [self.ROOT_URL + link['href'].replace('index.html', 'FullText.html') for link in div_elements]

    def _parse(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        div_elements = soup.find_all('div', {'class': 'docContents'})
        return [div_element.text for div_element in div_elements]

    async def _fetch_act_urls(self):
        async with aiohttp.ClientSession() as session:
            htmls = await asyncio.gather(*[self._fetch(url, session) for url in self.ACT_URLS])
        parsed_htmls = [self._parse_index(html) for html in htmls if html]
        return [item for sublist in parsed_htmls for item in sublist]

    async def _fetch_and_parse(self, page_link, session):
        logging.info(f'CRAWLING .... {page_link}')
        try:
            html = await self._fetch(page_link, session)
        except aiohttp.ClientResponseError() as e:
            logging.info(f"Error: {e}")
            return None  # or handle this case accordingly
        return {page_link: self._parse(html)}

    def crawl(self, local_cache: str = None):
        loop = asyncio.get_event_loop()
        logging.info('Fetching act urls...')
        act_urls = loop.run_until_complete(self._fetch_act_urls())
        logging.info(f'Fetched {len(act_urls)} act urls.')
        loop.run_until_complete(self._crawl(links=act_urls))


def main():
    crawler = ActCrawler()
    crawler.crawl()



if __name__ == "__main__":
    main()
