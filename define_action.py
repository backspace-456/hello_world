from extract_field import extract_field
import yaml

def define_actions(INDEX, index_, mappings):
	# 备份原有数据到当前目录下
	with open('/code/y/metadata/actions.yaml', 'r') as f:
		temp = f.read()
		with open('actions.yaml', 'w') as f1:
			f1.write(temp)
	with open('/code/y/metadata/actions.graphql', 'r') as f:
		temp = f.read()
		with open('actions.graphql', 'w') as f1:
			f1.write(temp)

	# 处理graphql
	with open('model_files/query_graphql_model.graphql','r')as f:
		add_query = f.read()
	add_query = add_query.replace('INDEX', INDEX)
	with open('model_files/graphql_model.graphql','r')as f:
		add_graphql = f.read()
	add_graphql = add_graphql.replace('INDEX', INDEX)
	with open('actions.graphql','r')as f:
		graphql = f.read()
	graphql = list(graphql)
	graphql.insert(13,add_query)
	graphql = ''.join(graphql)
	graphql += add_graphql
	add_graphql, all_string_type, all_num_type = extract_field(INDEX, mappings)
	graphql += add_graphql
	# 写入metadata
	with open('/code/y/metadata/actions.graphql','w') as f:
	# with open('actions.graphql','w') as f:
		f.write(graphql)
	

	# 处理yaml
	allow_list1 = []
	allow_list2 = []
	allower = input('If you want other user except \'admin\' to use this action\nthen input the users\' name. \nInput \'exit()\' to end\n')
	while allower != 'exit()' and allower != 'exit':
		allow_list1.append({'role':allower})
		allow_list2.append({'role':allower})
		allower = input()
	pack_yaml(allow_list1, allow_list2, INDEX, index_)
	return all_string_type, all_num_type



def pack_yaml(allow_list1, allow_list2, INDEX, index_):
	with open('model_files/actions_model.yaml') as f:
		docs = yaml.load_all(f, Loader=yaml.FullLoader)
		docs = list(docs)
		if len(allow_list1) != 0:
			docs[0][0]['permissions'] = allow_list1 
		docs[0][0]['definition']['handler'] = docs[0][0]['definition']['handler'].replace('index_', index_)
		docs[0][0]['name'] = docs[0][0]['name'].replace('INDEX', INDEX)
		
		if len(allow_list2) != 0:
			docs[0][1]['permissions'] = allow_list2
		docs[0][1]['definition']['handler'] = docs[0][1]['definition']['handler'].replace('index_', index_)
		docs[0][1]['name'] = docs[0][1]['name'].replace('INDEX', INDEX)
	with open('/code/y/metadata/actions.yaml') as f:
		docs1 = yaml.load_all(f, Loader=yaml.FullLoader)
		docs1 = list(docs1)
		docs1[0]['actions'].append(docs[0][0])

		docs1[0]['actions'].append(docs[0][1])

	with open('/code/y/metadata/actions.yaml', 'w') as f:
	# with open('actions.yaml', 'w') as f:
		yaml.dump(docs1[0], f)


