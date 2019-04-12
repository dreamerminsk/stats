import pickle
from datetime import datetime
from urllib.parse import urlparse, parse_qs

import requests
from bs4 import BeautifulSoup

import utils

LOGIN_URL = 'https://rutracker.org/forum/login.php'
TOPIC_URL = 'https://rutracker.org/forum/viewtopic.php?t='
USER_URL = 'https://rutracker.org/forum/profile.php?mode=viewprofile&u='
FORUM_URL = 'https://rutracker.org/forum/viewforum.php?f='


def load_cookies():
    with open('cookie.dat', 'rb') as f:
        cookies = pickle.load(f)
    return cookies


def save_cookies(cookies):
    with open('cookie.dat', 'wb') as f:
        pickle.dump(cookies, f)


def is_auth(doc):
    item = doc.select_one('.logged-in-as-uname')
    if item:
        return True
    else:
        return False


s = requests.Session()
s.cookies = load_cookies()


def login():
    res2 = s.post(LOGIN_URL, data={'login_username': 'dreamer.by', 'login_password': 'x1shT', 'login': 'вход'})
    doc = BeautifulSoup(res2.text, 'html.parser')
    form = doc.select_one('#login-form-full')
    if form:
        img = form.select_one('img')
        print(img.get('src'))
        cap = input('input captcha: ')
        ds = {}
        for v in form.select('input'):
            if v.get('name'):
                if v.get('value'):
                    ds[v.get('name')] = v.get('value')
                else:
                    ds[v.get('name')] = cap
        res2 = s.post('https://rutracker.org/forum/login.php', data=ds)
    save_cookies(s.cookies)


def get_page(ref):
    try:
        r = s.get(ref, timeout=24)
        doc = BeautifulSoup(r.text, 'html.parser')
        return (doc, None)
    except Exception as ex:
        return (None, ex)
    
    
class WebClient():
    def get_page(ref):
        try:
            r = s.get(ref, timeout=24)
            doc = BeautifulSoup(r.text, 'html.parser')
            return (doc, None)
        except Exception as ex:
            return (None, ex)    
    
    
    def load_cookies():
        with open('cookie.dat', 'rb') as f:
            cookies = pickle.load(f)
        return cookies


    def save_cookies(cookies):
        with open('cookie.dat', 'wb') as f:
            pickle.dump(cookies, f)


def get_forum(id):
    url = FORUM_URL + str(id)
    return get_page(url)


def get_topic(id):
    url = TOPIC_URL + str(id)
    return get_page(url)


def get_topic2(topic_id):
    url = TOPIC_URL + str(topic_id)
    doc, error = get_page(url)
    if error is not None:
        return (None, error)
    parser = TopicParser()
    topic = parser.parse(doc)
    topic['id'] = topic_id
    return (topic, None)


def get_user(id):
    url = USER_URL + str(id)
    return get_page(url)


class TopicParser:
    @staticmethod
    def get_title(doc):
        title = None
        t = doc.select_one('h1.maintitle')
        if t:
            title = t.text.strip()
        return title

    @staticmethod
    def get_forum(doc):
        forum = None
        for item in doc.select('table.w100 a'):
            q = urlparse(item.get('href')).query
            ps = parse_qs(q)
            if 'f' in ps:
                forum = ps['f'][0]
        return forum

    @staticmethod
    def get_seed(doc):
        seed = 0
        seed_item = doc.select_one('.seed b')
        if seed_item:
            seed = int(seed_item.text.strip())
        return seed

    @staticmethod
    def get_leech(doc):
        leech = 0
        leech_item = doc.select_one('.leech b')
        if leech_item:
            leech = int(leech_item.text.strip())
        return leech

    @staticmethod
    def get_published(doc):
        published = None
        pi = doc.select_one('p.post-time a')
        if pi:
            published = utils.parse_date(pi.text.strip())
        return published

    @staticmethod
    def get_last_modified(doc):
        lm = None
        lmi = doc.select_one('.posted_since')
        if lmi:
            idx = lmi.text.find('ред. ')
            if idx > 0:
                val = lmi.text[idx + 5:idx + 20]
                lm = utils.parse_date(val)
        return lm

    @staticmethod
    def get_hash(doc):
        tor_hash = None
        hi = doc.select_one('#tor-tor_hash')
        if hi:
            tor_hash = hi.text.strip()
        else:
            hi = doc.select_one('#tor-hash')
            if hi:
                tor_hash = hi.text.strip()
        return tor_hash

    @staticmethod
    def get_downloads(doc):
        downloads = 0
        for n in doc.select('li'):
            if n.text.startswith('Скачан'):
                downloads = utils.extract_int(n.text)
        return downloads

    @staticmethod
    def get_user(doc):
        user = 0
        for n in doc.select('a'):
            if n.text.startswith('[Профиль]'):
                q = urlparse(n.get('href')).query
                ps = parse_qs(q)
                if 'u' in ps:
                    user = ps['u'][0]
        return user

    def parse(self, doc):
        topic = dict()
        topic['forum'] = self.get_forum(doc)
        topic['title'] = self.get_title(doc)
        topic['seed'] = self.get_seed(doc)
        topic['leech'] = self.get_leech(doc)
        topic['published'] = self.get_published(doc)
        topic['last_modified'] = self.get_last_modified(doc)
        topic['hash'] = self.get_hash(doc)
        topic['downloads'] = self.get_downloads(doc)
        topic['last_checked'] = datetime.now()
        topic['user_id'] = self.get_user(doc)
        return topic
