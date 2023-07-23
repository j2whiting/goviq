import asyncio
import aiohttp
from bs4 import BeautifulSoup

from goviq.config.scrapers.parl_ca import ROOT_URL

def get_bill_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', class_='bill-details')
    return [link['href'] for link in links]

async def fetch_page(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers={'User-Agent': 'Mozilla/5.0'}) as response:
            if response.status == 200:
                return await response.text()
            else:
                raise aiohttp.ClientResponseError(
                    f"Failed to fetch page: {url}. Status code: {response.status}"
                )

async def get_all_pages(root_url):
    page = 1
    html_list = []
    while True:
        page_link = root_url.format(page)
        print(f'CRAWLING .... {page_link}')
        try:
            html = await fetch_page(page_link)
        except aiohttp.ClientResponseError as e:
            # Handle the error here (e.g., logging, retrying, etc.)
            print(f"Error: {e}")
            break  # Break the loop if there's an error

        bill_links = get_bill_links(html)
        print(html)
        if not bill_links:  # If there are no bill links, assume we reached the end
            break

        html_list.append(html)
        page += 1

    return html_list
def main():
    loop = asyncio.get_event_loop()
    html_list = loop.run_until_complete(get_all_pages(ROOT_URL))

    bill_links = []
    for html in html_list:
        bill_links.extend(get_bill_links(html))
    with open('bill_links.txt', 'w') as f:
        for link in bill_links:
            f.write(f'{link}\n')

if __name__ == '__main__':
    main()
