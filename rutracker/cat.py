import requests
from bs4 import BeautifulSoup

import source

req = requests.get('https://rutracker.org/')
doc = BeautifulSoup(req.text, 'html.parser')
for ref in doc.select('a'):
    if '?c=' in ref.get('href'):
        href = ref.get('href')
        cat = {}
        cat['id'] = href[href.find('?c=') + 3:]
        cat['title'] = ref.text.strip()
        source.insert_category(cat)
        print(cat)
