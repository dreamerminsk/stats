import requests
from bs4 import BeautifulSoup

from nnmclub.models import Category


async def get_forums(ref):
    forums = []
    s = requests.Session()
    try:
        r = s.get(ref, timeout=24)
        d = BeautifulSoup(r.text, 'html.parser')
        tables = d.select("td.leftnav > table.pline")
        for href in tables[1].select("td.row1 a.genmed"):
            forums.append(Category.parse(href))
        return forums
    except Exception as exc:
        print(exc)
        return None
