from abc import ABC, abstractmethod
from typing import List


class Preprocessor(ABC):
    _version = 1
    cache_path = None

    @abstractmethod
    def load(self, path: str, **kwargs):
        raise NotImplementedError()

    @abstractmethod
    def preprocess(self, document: List[dict], **kwargs) -> dict:
        """
        :param document: List of documents pulled from scraper. Each doc should be in the structure:
        {URL: HTML text}
        :param kwargs: Additional kwargs for preprocessing.
        :return: List of JSON serializable objects, where each key in the JSON corresponds to relevant metadata.
        """
        raise NotImplementedError()

    @abstractmethod
    def cache(self, **kwargs):
        raise NotImplementedError()
