import unittest

from goviq.scrapers.parl_ca import BillCrawler


class TestBillCrawler(unittest.TestCase):
    def setUp(self):
        self.crawler = BillCrawler()

    def test_fetch_bills(self):
        links = self.crawler.fetch_bills()
        self.assertIsInstance(links, list)
        self.assertTrue(len(links) > 0)

    async def test_parse(self):
        mock_html = """
        <html>
            <body>
                <a class="publication btn btn-primary" href="/DocumentViewer/en/44-1/bill/C-1/first-reading/page-1">Link</a>
            </body>
        </html>
        """
        html = await self.crawler._parse(mock_html)
        self.assertIsInstance(html, str)
        self.assertTrue(len(html) > 0)

    # TODO: Create fixture for testing caching with tempfile

