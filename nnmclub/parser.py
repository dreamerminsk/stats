import requests
from bs4 import BeautifulSoup

from nnmclub.models import Category


async def get_cats(ref):
    urls = []
    s = requests.Session()
    try:
        r = s.get(ref, timeout=24)
        d = BeautifulSoup(r.text, 'html.parser')
        tables = d.select("td.leftnav > table.pline")
        for href in tables[1].select("td.row1 a.genmed"):
            urls.append(Category.parse(href))
        return urls
    except Exception as exc:
        print(exc)
        return None
