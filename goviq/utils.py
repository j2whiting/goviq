from concurrent.futures import ProcessPoolExecutor
import datetime
import bs4
from langdetect import detect_langs
import json
from typing import List


def datestamp():
    """Return a datestamp string in the format YYYYMMDDHHMMSS"""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")


def dateparse(datestring):
    """Return a datetime object from a datestamp string in the format YYYYMMDDHHMMSS"""
    return datetime.datetime.strptime(datestring, "%Y%m%d%H%M%S")


def extract_html_text(html: str):
    soup = bs4.BeautifulSoup(html, 'html.parser')
    texts = soup.find_all(string=True)
    visible_texts = filter(
        lambda text: text.parent.name not in ['style', 'script', 'head', 'title', 'meta', '[document]'], texts)
    return " ".join(t.strip() for t in visible_texts if t.strip())


def load_json_docs(path: str):
    with open(path, 'r') as f:
        return json.load(f)


def find_language_transition(text, window_size=5000, step_size=3000, batch_size=10):
    num_windows = len(text) - window_size + 1
    transition_index = None
    min_diff = float('inf')

    with ProcessPoolExecutor() as executor:
        for i in range(0, num_windows, step_size):
            batch_windows = [text[i + j:i + j + window_size] for j in range(0, step_size, batch_size)]
            lang_probabilities_list = list(executor.map(detect_langs, batch_windows))

            for lang_probabilities in lang_probabilities_list:
                if len(lang_probabilities) >= 2:
                    diff = abs(lang_probabilities[0].prob - lang_probabilities[1].prob)

                    if diff < min_diff:
                        min_diff = diff
                        transition_index = i + window_size

    return transition_index


def split_document_at_language_transition(document, window_size=1000):
    transition_index = find_language_transition(document, window_size)

    if transition_index is not None:
        english_text = document[:transition_index]
        french_text = document[transition_index:]
        return english_text, french_text
    else:
        return document, None


def act_reference_count(bill: str, acts: List[str]):
    """Return the number of times each act is referenced in a bill. Return as a dictionary of act: count pairs"""
    act_cts = {}
    for act in acts:
        ct = bill.lower().count(act.lower())
        if ct > 0:
            act_cts[act] = ct
    return act_cts
