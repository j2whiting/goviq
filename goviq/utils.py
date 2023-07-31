import datetime
import bs4


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
