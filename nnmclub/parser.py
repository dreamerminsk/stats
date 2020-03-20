import requests
from bs4 import BeautifulSoup

from nnmclub.models import Forum


async def get_forums(ref):
    forums = []
    s = requests.Session()
    try:
        r = s.get(ref, timeout=24)
        d = BeautifulSoup(r.text, 'html.parser')
        tables = d.select("td.leftnav > table.pline")
        for href in tables[1].select("td.row1 a.genmed"):
            forums.append(Forum.parse(href))
        return forums
    except Exception as exc:
        print(exc)
        return None

async def get_torrents(forum):
    torrents = []
    s = requests.Session()
    try:
        ref = "http://nnmclub.to/forum/portal.php?c={}".format(forum.id)
        r = s.get(ref, timeout=24)
        d = BeautifulSoup(r.text, 'html.parser')
        tables = d.select("table.pline")
        for i, table in enumerate(tables):
            titles = table.select("td.pcatHead h2.substr a.pgenmed")
            if titles:
                torrents.append(Forum(id=-1, name=titles[0].get("title")))
        return torrents
    except Exception as exc:
        print(exc)
        return None
