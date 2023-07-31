from abc import ABC, abstractmethod
import aiohttp
import asyncio
import logging
from typing import Any


class Crawler(ABC):
    ROOT_URL = None
    _version = 1
    cache_path = None
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) " \
                 "AppleWebKit/605.1.15 (KHTML, like Gecko)" \
                 "Version/12.1.1 Safari/605.1.15"

    async def _fetch(self, url: str, session: aiohttp.ClientSession):
        async with session.get(url, headers={'User-Agent': self.user_agent}) as response:
            if response.status == 200:
                return await response.text()
            logging.warning(
                f"Failed to fetch page: {url} Status code: {response.status}"
            )
            return None

    @abstractmethod
    def _parse(self, **kwargs) -> Any:
        """
        :param kwargs:
        :return:
        """
        raise NotImplementedError()

    async def _fetch_and_parse(self, page_link, session):  # TODO: take this out of the class
        logging.info(f'CRAWLING .... {page_link}')
        try:
            html = await self._fetch(page_link, session)
        except aiohttp.ClientResponseError() as e:
            logging.info(f"Error: {e}")
            return None  # or handle this case accordingly
        return {page_link: await self._parse(html)}

    async def _crawl(self, links):
        async with aiohttp.ClientSession() as session:
            tasks = [self._fetch_and_parse(page_link, session) for page_link in links]
            return await asyncio.gather(*tasks)

    @abstractmethod
    def _cache(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def crawl(self):
        raise NotImplementedError()
