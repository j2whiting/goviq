import os
import regex as re
import requests
import tqdm
from typing import List

from goviq.entities.preprocessor import Preprocessor
from goviq.config.local_cache import LOCAL_CACHE
from goviq.utils import split_document_at_language_transition


class ActCAPreprocessor(Preprocessor):
    version = 1
    # Note: This regex seems to work for all acts except for 4 out of the ~900ish total federal acts.
    # I have not checked for false positives yet
    act_title_regex = r'^([A-Z][a-z].+?)(?=\s?(?:R\.S\.C\.|S\.C\.|Agreements and ConventionsAssented))'

    def __init__(self, local_cache: str = None):
        self.local_cache = local_cache if local_cache else LOCAL_CACHE

    def _parse_title(self, html_body: str) -> str:
        title = re.findall(self.act_title_regex, html_body, re.MULTILINE)
        return title[0].strip() if title else None

    def preprocess(self, acts_path: str, cache: bool = True) -> List[dict]:
        docs = self.load(acts_path)
        processed_docs = []
        for doc in tqdm.tqdm(docs):  # TODO: Add multiprocessing
            json_doc = {}
            url = list(doc.keys())[0]
            html_body = list(doc.values())[0][0]
            # TODO: Fix this, langdetect not playing nicely with multiprocessing.
            # html_body, _ = split_document_at_language_transition(html_body)
            title = self._parse_title(html_body)
            if title:
                json_doc['title'] = title
            json_doc['url'] = url
            json_doc['body'] = html_body
            processed_docs.append(json_doc)
        if cache:
            out_path = os.path.join(self.local_cache, 'processed_' + acts_path)
            self.cache(processed_docs, path=out_path)
        return processed_docs

    # TODO: Figure out how to parse sections and subsections from the HTML. We need to map amendments from bills onto sections of the acts for context.