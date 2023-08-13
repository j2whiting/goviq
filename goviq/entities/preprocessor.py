from abc import ABC, abstractmethod
import json
import logging
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
    def preprocess(self, **kwargs) -> List[dict]:
        """
        :return: List of JSON serializable objects, where each key in the JSON corresponds to relevant metadata.
        """
        raise NotImplementedError()

    def cache(self, docs: List[dict], path) -> None:
        out_path = os.path.join(self.local_cache, path)
        with open(out_path, 'w') as f:
            logging.info(f'Writing {type(self)} output to {out_path}')
            json.dump(docs, f)
