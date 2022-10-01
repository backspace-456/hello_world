import os
# 恢复上一级

def recover():
	with open('/home/zjchen/bin/hasura_middle/actions.yaml', 'r') as f:
		yaml = f.read()
		with open('/home/zjchen/bin/y/metadata/actions.yaml', 'w') as f1:
			f1.write(yaml)
	with open('/home/zjchen/bin/hasura_middle/actions.graphql', 'r') as f:
		graphql = f.read()
		with open('/home/zjchen/bin/y/metadata/actions.graphql', 'w') as f1:
			f1.write(graphql)
	os.system('./final.sh')
