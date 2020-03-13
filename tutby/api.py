from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

s = requests.Session()


def get_page(ref):
    try:
        r = s.get(ref, timeout=24)
        return BeautifulSoup(r.text, 'html.parser'), None
    except Exception as exc:
        return None, exc


doc, ex = get_page('http://tut.by/')
for href in doc.select("a[href*='tut.by']"):
    parsed_uri = urlparse(href.get('href'))
    print(parsed_uri.netloc)
for href in doc.select("img[src*='.jpg']"):
    print(href)
