from abc import abstractmethod
from typing import Any


class Crawler:
    ROOT_URL = None
    _version = 1
    cache_path = None
    user_agent = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) " \
                 "AppleWebKit/605.1.15 (KHTML, like Gecko)" \
                 "Version/12.1.1 Safari/605.1.15"

    @abstractmethod
    async def _fetch(self, **kwargs) -> str:
        """
        Fetches text from a url.
        :param kwargs:
        :return: text body from URL
        """
        raise NotImplementedError()

    @abstractmethod
    async def _parse(self, **kwargs) -> Any:
        """
        :param kwargs:
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    async def _crawl(self, **kwargs):
        """
        Crawls list of URLs using fetch and parse.
        :param kwargs:
        :return:
        """
        raise NotImplementedError()

    @abstractmethod
    def _cache(self, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def crawl(self):
        raise NotImplementedError()