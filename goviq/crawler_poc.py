import argparse
import os

from goviq.scrapers.parl_ca import BillCrawler
from goviq.scrapers.acts_ca import ActCrawler

"""
This is a proof of concept for the crawler. It is not used in production.
This will write all crawled canadian acts and federal bills to the output directory.
"""


def main():
    parser = argparse.ArgumentParser(description='Scrape Canadian legislation.')
    parser.add_argument('--output_dir', help='Directory to write output to.')
    args = parser.parse_args()
    output_dir = args.output_dir
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    bill_crawler = BillCrawler(local_cache=output_dir)
    bill_crawler.crawl()
    act_crawler = ActCrawler(local_cache=output_dir)
    act_crawler.crawl()


if __name__ == "__main__":
    main()
