import logging
import multiprocessing
from typing import List

from goviq.config.local_cache import LOCAL_CACHE
from goviq.entities.preprocessor import Preprocessor
from goviq.utils import extract_html_text

logging.getLogger().setLevel(logging.INFO)


class ParlCAPreprocessor(Preprocessor):
    """
    Preprocesses the raw data from the Parliament of Canada.
    """
    _version = 1

    def __init__(self, local_cache: str = None):
        self.local_cache = local_cache if local_cache else LOCAL_CACHE

    @staticmethod
    def _mpreprocess(documents: List[dict], num_processes) -> List[dict]:
        html_texts = [list(i.values())[0] for i in documents]
        urls = [list(i.keys())[0] for i in documents]

        # Create a pool of worker processes
        with multiprocessing.Pool(processes=num_processes) as pool:
            # Use map to apply the extract_text function to each chunk of HTML texts
            # The results will be stored in a list
            extracted_texts = pool.map(extract_html_text, html_texts)
        # extracted_texts = [text for sublist in extracted_texts for text in sublist]
        return [{k: v} for k, v in dict(zip(urls, extracted_texts)).items()]

    def preprocess(self, path: str, num_processes=4) -> None:
        documents = self.load(path)
        documents = self._mpreprocess(documents, num_processes)
        out_path = 'processed_' + path.split('/')[-1]
        self.cache(docs=documents, path=out_path)
