"""Base Scraping Class — uses cloudscraper to bypass bot protection"""
from __future__ import print_function
from __future__ import absolute_import
import random
import cloudscraper

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

MAX_RETRIES = 3

BROWSER_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Cache-Control': 'max-age=0',
}


def random_line():
    """Gets a random User-Agent string from local DB file."""
    try:
        with open("storage/user-agents.db") as afile:
            line = next(afile)
            for num, aline in enumerate(afile):
                if random.randrange(num + 2):
                    continue
                line = aline
        return line.strip()
    except Exception:
        return ('Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/122.0.0.0 Safari/537.36')


def make_scraper():
    """Create a cloudscraper instance that mimics a real Chrome browser."""
    return cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'mobile': False}
    )


class PageGrabber:
    """Base class providing HTTP functionality to all plugin modules."""

    def __init__(self):
        self.info_dict = {}
        self.info_list = []
        self.ua = random_line()
        self._scraper = make_scraper()

    def _headers(self, referer=None):
        h = dict(BROWSER_HEADERS)
        h['User-Agent'] = self.ua
        if referer:
            h['Referer'] = referer
        return h

    def get_source(self, url, referer=None):
        """Returns page source as a UTF-8 string, bypassing Cloudflare."""
        headers = self._headers(referer)
        for attempt in range(MAX_RETRIES):
            try:
                resp = self._scraper.get(url, headers=headers, timeout=15, allow_redirects=True)
                return resp.text
            except Exception:
                if attempt == MAX_RETRIES - 1:
                    return ''
        return ''

    def post_data(self, url, data, referer=None):
        """Sends a POST request, returns response text."""
        headers = self._headers(referer)
        for attempt in range(MAX_RETRIES):
            try:
                resp = self._scraper.post(url, headers=headers, data=data, timeout=15, allow_redirects=True)
                return resp.text
            except Exception:
                if attempt == MAX_RETRIES - 1:
                    return ''
        return ''

    def get_json(self, url, headers=None):
        """GET request that returns parsed JSON, or None on failure."""
        import requests
        h = self._headers()
        if headers:
            h.update(headers)
        for attempt in range(MAX_RETRIES):
            try:
                resp = self._scraper.get(url, headers=h, timeout=15)
                return resp.json()
            except Exception:
                if attempt == MAX_RETRIES - 1:
                    return None
        return None

    def write_file(self, data, filename):
        """Writes data string to disk."""
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(data)

    def get_dom(self, source):
        """Returns a BeautifulSoup DOM (lxml parser)."""
        from bs4 import BeautifulSoup
        return BeautifulSoup(source, 'lxml')

    def get_html(self, source):
        """Returns a BeautifulSoup DOM (html.parser)."""
        from bs4 import BeautifulSoup
        return BeautifulSoup(source, 'html.parser')
