# Scraping the twiki home page.
# url = https://twiki.cern.ch/twiki/bin/viewauth/LHCb/WebHome

import requests
from datetime import datetime
import json
import csv
from bs4 import BeautifulSoup
import getpass 
from urllib.parse import urljoin
import os

class CERNLHCbScraper:
    def __init__(self):
        self.session = requests.session()
        self.base_url = "https://twiki.cern.ch"
        self.authenticated = False


        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        })

    def login_with_cookies(self, cookies_dict=None):
        # trying to login using cookies from browser session

