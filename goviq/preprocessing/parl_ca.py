import logging
import multiprocessing
import regex as re
import requests
import tqdm
from typing import List

from goviq.config.local_cache import LOCAL_CACHE
from goviq.entities.preprocessor import Preprocessor
from goviq.utils import extract_html_text, act_reference_count

logging.getLogger().setLevel(logging.INFO)


class ParlCAPreprocessor(Preprocessor):
    """
    Preprocesses the raw data from the Parliament of Canada.
    """
    _version = 1
    dropped_pattern = r'This bill was not proceeded with on | This bill was dropped from the'
    defeated_pattern = r'This bill was defeated on'
    royal_assent_pattern = r'This bill received royal assent on'

    def __init__(self, local_cache: str = None):
        self.local_cache = local_cache if local_cache else LOCAL_CACHE

    def _parse_final_status(self, url: str) -> str:
        r = requests.get(url)
        if r.status_code != 200:
            raise Exception(f'Could not retrieve {url} with status code {r.status_code}')
        body = r.text
        if re.search(self.dropped_pattern, body):
            return 'dropped'
        elif re.search(self.defeated_pattern, body):
            return 'defeated'
        elif re.search(self.royal_assent_pattern, body):
            return 'royal_assent'
        else:
            return 'in_progress'

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
        return [{'link': k, 'body': v} for k, v in dict(zip(urls, extracted_texts)).items()]

    def preprocess(self, bills_path: str, preprocessed_acts_path: str, num_processes=4) -> List[dict]:
        preprocessed_bills = []
        bills = self.load(bills_path)
        act_docs = self.load(preprocessed_acts_path)
        act_names = []
        for i in act_docs:
            if 'title' in i:
                act_names.append(i['title'])
        bills = self._mpreprocess(bills, num_processes)
        for bill in tqdm.tqdm(bills):  # TODO: Add multiprocessing, currently a bottleneck... ~2 minutes to run.
            bill.update({'status': self._parse_final_status(bill['link'])})
            bill.update({'act_mentions': act_reference_count(bill['body'], act_names)})
            preprocessed_bills.append(bill)
        out_path = 'processed_' + bills_path.split('/')[-1]
        self.cache(docs=preprocessed_bills, path=out_path)
        return preprocessed_bills
