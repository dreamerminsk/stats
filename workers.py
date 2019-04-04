from datetime import datetime
from time import sleep
from urllib.parse import urlparse, parse_qs

import requests
from PySide2.QtCore import QObject, Signal
from bs4 import BeautifulSoup

import rutracker
from source import DataSource


class RssWorker(QObject):
    processed = Signal(int, int)
    finished = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.ds = DataSource()
        self.terminating = False

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
        while not self.terminating:
            try:
                self.process()
            except Exception as e:
                print('RSS EXCEPTION: ' + str(e))
        self.finished.emit()

    def finish(self):
        self.terminating = True

    def process(self):
        torrents = 0
        f = self.ds.get_forum_to_scan()
        print('RSS: ' + str(f))
        if 'id' not in f:
            sleep(4)
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
        print(f['title'] + ': ' + str(torrents))
        self.processed.emit(f['id'], torrents)
        if torrents > 0:
            delta = delta * 0.9
            self.ds.update_rss(f['id'], delta, datetime.now())
        else:
            delta = delta * 1.1
            self.ds.update_rss(f['id'], delta, datetime.now())
        sleep(4)


class NewTorrentWorker(QObject):
    processed = Signal(dict)
    finished = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.ds = DataSource()
        self.terminating = False
        self.torrents = 0

    def run(self):
        while not self.terminating:
            try:
                self.process()
            except Exception as e:
                print('ADDING TORRENT EXCEPTION: ' + str(e))
        self.finished.emit()

    def finish(self):
        self.terminating = True

    def process(self):
        t = self.ds.get_torrent()
        if 'id' not in t:
            return
        topic, error = rutracker.get_topic2(t['id'])
        if error is not None:
            print(error)
            return
        self.ds.insert_torrent(topic)
        self.torrents += 1
        self.processed.emit(topic)
        sleep(8)


class UpdateTorrentWorker(QObject):
    processed = Signal(dict)
    finished = Signal()

    def __init__(self):
        QObject.__init__(self)
        self.ds = DataSource()
        self.terminating = False
        self.torrents = 0

    def run(self):
        while not self.terminating:
            try:
                self.process()
            except Exception as e:
                print('ADDING TORRENT EXCEPTION: ' + str(e))
        self.finished.emit()

    def finish(self):
        self.terminating = True

    def process(self):
        t = self.ds.get_check_torrent()
        if 'id' not in t:
            return
        topic, error = rutracker.get_topic2(t['id'])
        if error is not None:
            print(error)
            return
        if not topic['title']:
            topic['title'] = t['title']
        if t['seed'] > topic['seed']:
            topic['seed'] = t['seed']
        if t['leech'] > topic['leech']:
            topic['leech'] = t['leech']
        if t['downloads'] > topic['downloads']:
            topic['downloads'] = t['downloads']
        self.ds.insert_torrent(topic)
        self.torrents += 1
        self.processed.emit(topic)
        sleep(8)
