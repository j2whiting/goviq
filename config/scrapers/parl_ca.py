"""
Configuration for the parl.ca scraper. This scraper is used to scrape bills in current session of parliament.
"""
import os
from bs4 import BeautifulSoup
ROOT_URL = 'https://www.parl.ca/legisinfo/en/bills?page={}'  # String format in page number

# Write a functon that returns each bill link: /legisinfo/en/bill/44-1/s-1 where the final number in the url is the bill number which is variable. The function must accept the raw htlm for the entire webpage.
def get_bill_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    links = soup.find_all('a', class_='title')
    return [link['href'] for link in links if link['href'].startswith('/legisinfo/en/bill')]


