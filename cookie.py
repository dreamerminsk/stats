import requests
import requests.utils
import pickle

dict = {'bb_ssl':'1', 'bb_session': '0-18468363-LL5xK152j7wt7ihMtqsY'}
cj = requests.utils.cookiejar_from_dict(dict)
with open('cookie.dat', 'wb') as f:
    pickle.dump(cj, f)
with open('cookie.dat', 'rb') as f:
    cj = pickle.load(f)
    print(cj)
