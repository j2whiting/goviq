import json
import multiprocessing
from typing import List

from goviq.config.local_cache import LOCAL_CACHE
from goviq.entities.preprocessor import Preprocessor
from goviq.utils import datestamp, extract_html_text


class ParlCAPreprocessor(Preprocessor):
    """
    Preprocesses the raw data from the Parliament of Canada.
    """
    _version = 1

    def __init__(self, local_cache: str = None):
        self.local_cache = local_cache if local_cache else LOCAL_CACHE

    def load(self, **kwargs):
        pass

    @staticmethod
    def _mpreprocess(documents: List[dict], num_processes):
        html_texts = [list(i.values())[0] for i in documents]
        urls = [list(i.keys())[0] for i in documents]

        # Create a pool of worker processes
        with multiprocessing.Pool(processes=num_processes) as pool:
            # Use map to apply the extract_text function to each chunk of HTML texts
            # The results will be stored in a list
            extracted_texts = pool.map(extract_html_text, html_texts)
        # extracted_texts = [text for sublist in extracted_texts for text in sublist]
        return dict(zip(urls, extracted_texts))

    def cache(self, documents: dict, filename='bill_text_procesed') -> None:
        filepath = f"{self.local_cache}/{filename}_{datestamp()}"
        with open(f'{filepath}.json', 'w') as f:
            json.dump(documents, f)

    def preprocess(self, documents: List[dict], filename='bill_text_processed', num_processes=4) -> None:
        documents = self._mpreprocess(documents, num_processes)
        self.cache(documents, filename)
