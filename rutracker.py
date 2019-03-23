import pickle

import requests
from bs4 import BeautifulSoup

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
        print(res2.text)
    save_cookies(s.cookies)
    print(load_cookies())


def get_page(ref):
    try:
        r = s.get(ref, timeout=24)
        doc = BeautifulSoup(r.text, 'html.parser')
        return (doc, None)
    except Exception as ex:
        return (None, ex)


def get_forum(id):
    url = FORUM_URL + str(id)
    return get_page(url)


def get_topic(id):
    url = TOPIC_URL + str(id)
    return get_page(url)


def get_user(id):
    url = USER_URL + str(id)
    return get_page(url)
