from datetime import datetime
from urllib.parse import urlparse, parse_qs

import requests
from PySide2.QtCore import QObject, Signal
from bs4 import BeautifulSoup

from source import DataSource


class RssWorker(QObject):
    finish = Signal(dict)

    def __init__(self):
        QObject.__init__(self)
        self.ds = DataSource()

    def get_page(self, ref):
        try:
            r = requests.get(ref, timeout=24)
            doc = BeautifulSoup(r.text, 'html.parser')
            return doc, None
        except Exception as ex:
            return None, ex

    def get_rss(self, forum):
        ref = 'http://feed.rutracker.cc/atom/f/' + str(forum['id']) + '.atom'
        (doc, error) = self.get_page(ref)
        return doc, error

    def run(self):
        while True:
            self.process()

    def process(self):
        torrents = 0
        f = self.ds.rss()
        if 'id' not in f:
            return
        doc, error = self.get_rss(f)
        if error is not None:
            print(error)
        for entry in doc.find_all('entry'):
            url = entry.find('link')
            q = urlparse(url.get('href')).query
            ps = parse_qs(q)
            torrent = (ps['t'][0], f['id'], entry.find('title').text,)
            if self.ds.save_torrent(torrent):
                torrents += 1
        delta = f['delta']
        if torrents > 0:
            self.rss_total += torrents
            delta = delta * 0.9
            self.ds.update_rss(f['id'], delta, datetime.now())
        else:
            delta = delta * 1.1
            self.ds.update_rss(f['id'], delta, datetime.now())
