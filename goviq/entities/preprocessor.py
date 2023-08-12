from abc import ABC, abstractmethod
import json
import os
from typing import List

from goviq.utils import load_json_docs


class Preprocessor(ABC):
    _version = 1
    local_cache = None

    @staticmethod
    def load(path: str) -> List[dict]:
        return load_json_docs(path)

    @abstractmethod
    def preprocess(self, document: List[dict], **kwargs) -> dict:
        """
        :param document: List of documents pulled from scraper. Each doc should be in the structure:
        {URL: HTML text}
        :param kwargs: Additional kwargs for preprocessing.
        :return: List of JSON serializable objects, where each key in the JSON corresponds to relevant metadata.
        """
        raise NotImplementedError()

    def cache(self, docs: List[dict], path) -> None:
        with open(os.path.join(self.local_cache, path), 'w') as f:
            json.dump(docs, f)
