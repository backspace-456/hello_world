import json
import requests

host = "https://developer:dev@hitnslab@es.database.hitwh.net.cn:9002/"
header = {'Content-Type': 'application/json'}
index_name = 'tryes-1'
resp = requests.get(url = host + index_name, headers=header)
if resp.status_code == 200:
  info = json.loads(resp.text)
  print(info[index_name]['mappings'])
  ss = json.dumps(info)
  print(ss)
