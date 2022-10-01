import json
from create_index import create_index
from define_action import define_actions
import os
from from_index_already import from_index_already, get_index_mappings
from recover import recover

# grapgql中不能出现- . 等特殊符号
def predeal_index_name(index_name):
	if '-' in index_name:
		index_name = index_name.replace('-', '_')
		index_name = index_name.replace('.', '')
	return index_name

def choose_mode():
	print('Please choose mode between from_create_index and from_index_already_have\n')
	mode = int(input('1 for from_create_index and 2 for from_index_already_have\nYour mode:'))
	# from_create_index
	if mode == 1:
		index_name = input("index_name:")
		filepath = input("index_mappings_path:")
		with open(filepath, 'r') as f:
			mappings = json.load(f)
		index_name_graphql = predeal_index_name(index_name)
		all_string_type, all_num_type = define_actions(index_name_graphql, index_name, mappings)
		# 创建对应索引，并将mappings存入es，以及可供搜索的字段数组
		if create_index(index_name, filepath, all_string_type, all_num_type):
			os.system('./final.sh')
			
		else:
			recover()
			
	# from_index_already
	elif mode == 2:
		index_name = input("index_name:")
		mappings = get_index_mappings(index_name)
		index_name_graphql = predeal_index_name(index_name)
		all_string_type, all_num_type = define_actions(index_name_graphql, index_name, mappings)
		# 创建对应索引，并将mappings存入es，以及可供搜索的字段数组
		if from_index_already(index_name, mappings, all_string_type, all_num_type):
			os.system('./final.sh')
			
		else:
			recover()
	else:
		print('Your input wrong mode_number. Please try it later!')

