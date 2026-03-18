"""Base Scraping Class"""
from __future__ import print_function
from __future__ import absolute_import
import requests
import random
from bs4 import BeautifulSoup

try:
    import __builtin__ as bi
except ImportError:
    import builtins as bi

import json

MAX_RETRIES = 3


def random_line():  # Gets random User-Agent string from local DB file
    afile = open("storage/user-agents.db")
    line = next(afile)
    for num, aline in enumerate(afile):
        if random.randrange(num + 2):
            continue
        line = aline
    return line.strip()


class PageGrabber:  # base function to import request functionality in modules
    """Base PageGrabber Class"""
    def __init__(self):  # Initialize defaults as needed
        self.info_dict = {}
        self.info_list = []
        self.ua = random_line()

    def get_source(self, url):  # Returns source code from given URL
        headers = {"User-Agent": self.ua}
        requests.packages.urllib3.disable_warnings()
        for attempt in range(MAX_RETRIES):
            try:
                results = requests.get(
                    url,
                    headers=headers,
                    timeout=10,
                    verify=False,
                    allow_redirects=True
                ).text
                return results.encode('ascii', 'ignore').decode("utf-8")
            except Exception:
                if attempt == MAX_RETRIES - 1:
                    return ""
        return ""

    def post_data(self, url, data):  # Sends POST request of given DATA, URL
        headers = {"User-Agent": self.ua}
        requests.packages.urllib3.disable_warnings()
        for attempt in range(MAX_RETRIES):
            try:
                results = requests.post(
                    url,
                    headers=headers,
                    timeout=10,
                    verify=False,
                    allow_redirects=True,
                    data=data
                ).text
                return results.encode('ascii', 'ignore').decode("utf-8")
            except Exception:
                if attempt == MAX_RETRIES - 1:
                    return ""
        return ""

    def write_file(self, data, filename):  # Writes data to disk
        with open(filename, 'w') as f:
            f.write(data)

    def get_dom(self, source):  # Returns BeautifulSoup DOM
        return BeautifulSoup(source, 'lxml')

    def get_html(self, source):  # Returns BeautifulSoup DOM
        return BeautifulSoup(source, 'html.parser')
