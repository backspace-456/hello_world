import json
import requests

# ol
# 命名不要有-
# mappings_path
def create_index(index_name, filepath, all_string_type, all_num_type):
	with open(filepath,'r') as f:
		# 读出字典格式
		mappings = json.load(f)
	host = "https://developer:dev@hitnslab@es.database.hitwh.net.cn:9002/"
	header = {'Content-Type': 'application/json'}
	try:
		resp = requests.put(url=host + index_name, data=json.dumps(mappings), headers=header)
		if resp.status_code == 200:
			print("success")
			# 存到hasura_index_mappings这个索引中去
			tt1 = {"index_name":index_name, "mappings": json.dumps(mappings), "all_string_type": all_string_type, "all_num_type": all_num_type}
			resp1 = requests.post(url=host + 'hasura_index_mappings/_doc', data=json.dumps(tt1), headers=header)
			if resp1.status_code == 200:
				print('success_for_insert_mappings!\n')
			return True
		else:
			print(resp1.text)
			return False
	except Exception as E:
		print(E.__str__())
		print("wrong")




