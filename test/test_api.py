import time
import dateutil.parser
import requests

api_url = 'http://api.enermed.it'
payload = {'api_key': '34bb672e', 'secret_key': '1b6211e5b9f4'}
r = requests.get(api_url + '/auth', params=payload)
r.raise_for_status()
print "##### Token:"
print r.text

valid_token = r.json()['token']
print valid_token

payload = {'token': valid_token, 'zone_id': 'L'}
r = requests.get(api_url + '/grid/stats', params=payload)

print "##### Grid Statistics:"
print r.json()


payload = {'token': valid_token, 'id': '110451548155'}
r = requests.get(api_url + '/contract/energia24h', params=payload)

print "##### Grid Statistics:"
print r.json()
