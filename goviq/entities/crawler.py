import asyncio
import aiohttp
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List

logging.getLogger().setLevel(logging.INFO)

class Crawler(ABC):
    """
    Base crawler providing asynchronous fetching and parsing.
    Subclasses must implement _parse (async) and _cache.
    """
    user_agent = (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_5) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) "
        "Version/12.1.1 Safari/605.1.15"
    )

    def __init__(self, max_concurrent_tasks: int = 50):
        """
        :param max_concurrent_tasks: Limits the number of concurrent fetches.
        """
        self.semaphore = asyncio.Semaphore(max_concurrent_tasks)

    async def _fetch(self, url: str, session: aiohttp.ClientSession) -> str | None:
        """
        Asynchronously fetches the text content of a URL.
        Returns None if any network error or non-200 status occurs.
        """
        try:
            async with session.get(url, headers={"User-Agent": self.user_agent}) as resp:
                if resp.status == 200:
                    return await resp.text()
                else:
                    logging.warning(f"Fetch failed ({resp.status}) for {url}")
                    return None
        except aiohttp.ClientError as e:
            logging.warning(f"Client error fetching {url}: {e}")
            return None

    @abstractmethod
    async def _parse(self, html: str) -> Any:
        """
        Asynchronously parses the fetched HTML content and returns structured data.
        Must be implemented by subclass.
        """
        raise NotImplementedError()

    async def _fetch_and_parse(self, url: str, session: aiohttp.ClientSession) -> Dict[str, Any] | None:
        """
        Fetches the given URL and then calls the subclass's _parse method on the HTML.
        Returns a dict {url: parsed_data} or None if something failed.
        """
        async with self.semaphore:
            logging.info(f"Crawling: {url}")
            html = await self._fetch(url, session)
            if html is None:
                return None
            parsed_data = await self._parse(html)
            return {url: parsed_data}

    async def _crawl(self, links: List[str]) -> List[Dict[str, Any]]:
        """
        Crawls all given links (fetch + parse), returning a list of {url: parsed_data} dicts.
        Skips any link that fails.
        """
        results = []
        connector = aiohttp.TCPConnector(limit=50)  # Adjust limit as needed
        async with aiohttp.ClientSession(connector=connector) as session:
            tasks = [self._fetch_and_parse(link, session) for link in links]
            raw_results = await asyncio.gather(*tasks, return_exceptions=True)

        for item in raw_results:
            if isinstance(item, Exception):
                # Log the exception but continue
                logging.error(f"Task raised an exception: {item}")
            elif item is not None:
                results.append(item)

        return results

    @abstractmethod
    def _cache(self, data: List[Dict[str, Any]], filename: str = "data") -> None:
        """
        Persists the crawler's results to local storage.
        Must be implemented by subclass.
        """
        raise NotImplementedError()

    @abstractmethod
    def crawl(self) -> None:
        """
        Initiates the entire crawling process (synchronously).
        Must be implemented by subclass.
        """
        raise NotImplementedError()
