import json
import requests

host = "https://developer:dev@hitnslab@es.database.hitwh.net.cn:9002/"
header = {'Content-Type': 'application/json'}

def get_index_mappings(index_name):
    try:
        resp = requests.get(url = host + index_name, headers=header)
        if resp.status_code == 200:
            info = json.loads(resp.text)
            mappings = info[index_name]
            print('get %s successfully!\n' % index_name)
            return mappings
    except Exception as E:
	    print(E.__str__())

def from_index_already(index_name, mappings, all_string_type, all_num_type):
    # 存到hasura_index_mappings这个索引中去
    tt1 = {"index_name":index_name, "mappings": json.dumps(mappings), "all_string_type": all_string_type, "all_num_type": all_num_type}
    resp1 = requests.post(url=host + 'hasura_index_mappings/_doc', data=json.dumps(tt1), headers=header)
    count = 1
    while count <= 3:
        if resp1.status_code == 200 or resp1.status_code == 201:
            print('success_for_insert_mappings!')
            return True
        elif resp1.status_code == 429:
            count += 1
            resp1 = requests.post(url=host + 'hasura_index_mappings/_doc', data=json.dumps(tt1), headers=header)
    print(resp1.status_code)
    print('wrong_for_insert_mappings!')
    print(resp1.text)
    return False