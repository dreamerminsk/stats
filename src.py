import source
from simple_rest_client.api import API
api = API(
    api_root_url='http://p29271es.bget.ru/api/rt/',
    params={},
    headers={'user-agent': 'Mozilla/5.0 (BB10; Kbd) AppleWebKit/537.35+ (KHTML, like Gecko) Version/10.3.3.2205 Mobile Safari/537.35+',},
    timeout=2,
    append_slash=False,
    json_encode_body=True,)
api.add_resource(resource_name='categories') 

api.add_resource(resource_name='forums') 

def insert(forum):
    try:
        r = api.forums.create(body=forum)
        print(r.status_code)
        if r.status_code < 400:
            print(r.body)
    except Exception as e:
        print(e)
    


fs = source.get_forums()
for f in fs:
    d = {}
    d['id'] = f['id']
    d['category_id'] = f['category']
    d['parent_id'] = f['parent']
    d['title'] = f['title']
    d['subscribed'] = f['subscribed']
    d['last_scanned_page'] = f['last_scanned_page']
    print(d)
    insert(d)