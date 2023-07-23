import requests
from bs4 import BeautifulSoup
from config import ROOT_URL


def get_bill_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', class_='title')
    return [link['href'] for link in links if link['href'].startswith('/legisinfo/en/bill')]


def fetch_page(url):
    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code == 200:
        return response.text
    return None


async def get_all_pages(root_url):
    page = 1
    html_list = []
    while True:
        html = await fetch_page(root_url.format(page))
        if html is None:
            break
        html_list.append(html)
        page += 1
    return html_list


def main():
    html_list = get_all_pages(ROOT_URL)
    bill_links = []
    for html in html_list:
        bill_links.extend(get_bill_links(html))
    with open('bill_links.txt', 'w') as f:
        for link in bill_links:
            f.write(f'{link}\n')


# now define the argparser and if name is main loop
if __name__ == '__main__':
    main()