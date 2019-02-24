from simple_rest_client.api import API
api = API(
    api_root_url='http://p29271es.bget.ru/api/rt/',
    params={},
    headers={'user-agent': 'Mozilla/5.0 (BB10; Kbd) AppleWebKit/537.35+ (KHTML, like Gecko) Version/10.3.3.2205 Mobile Safari/537.35+',},
    timeout=2,
    append_slash=False,
    json_encode_body=True,)
api.add_resource(resource_name='categories') 
r = api.categories.list()
print(r.body)
r = api.categories.create(body={'id': 999, 'title': 'test',})
print(r.status_code)
print(r.body)