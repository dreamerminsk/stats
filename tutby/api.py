from time import sleep
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


urls = {'http://tut.by/'}
hosts = set()
while len(urls) > 0:
    url = urls.pop()
    print("\t\t\t{} - {}".format(len(urls), url))
    sleep(4)
    doc, ex = get_page(url)
    if ex is not None:
        continue
    print("\t\t\t{}".format(doc.select_one('title').text))
    sleep(4)
    for href in doc.select("a[href*='news.tut.by']"):
        parsed_uri = urlparse(href.get('href'))
        urls.add(href.get('href'))
        hosts.add(parsed_uri.netloc)
    for host in hosts:
        print(host)
    print("------------------------")
    for href in doc.select("img[alt*='Фото']"):
        print("{} - {}".format(href.get("alt"), href.get("src")))
