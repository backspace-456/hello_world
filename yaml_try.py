#!/usr/bin/env python3

import yaml
def ff2(lis1,lis2):

    with open('/home/zjchen/bin/hasura_middle/model_files/actions_model.yaml') as f:

        docs = yaml.load_all(f, Loader=yaml.FullLoader)

        docs = list(docs)
        print(type(docs[0]))
        docs[0][0]['permissions'] = lis1
        docs[0][0]['definition']['handler'] = docs[0][0]['definition']['handler'].replace('index_', 'tryes-1')
        docs[0][0]['name'] = docs[0][0]['name'].replace('INDEX', 'tryes_1')

        docs[0][1]['permissions'] = lis2
        docs[0][1]['definition']['handler'] = docs[0][0]['definition']['handler'].replace('index_', 'tryes-1')
        docs[0][1]['name'] = docs[0][0]['name'].replace('INDEX', 'tryes_1')
        print(yaml.dump(docs))

def ff1(lis):

    with open('/home/zjchen/bin/hasura_middle/model_files/actions_model.yaml') as f:

        docs = yaml.load_all(f, Loader=yaml.FullLoader)

        docs = list(docs)
        print(type(docs[0]))
        docs[0][0].setdefault('permissions',lis)
        docs[0][0]['definition']['handler'] = docs[0][0]['definition']['handler'].replace('index_', 'tryes-1')
        docs[0][0]['name'] = docs[0][0]['name'].replace('INDEX', 'tryes_1')

        docs[0][1].setdefault('permissions',lis[:])
        docs[0][1]['definition']['handler'] = docs[0][0]['definition']['handler'].replace('index_', 'tryes-1')
        docs[0][1]['name'] = docs[0][0]['name'].replace('INDEX', 'tryes_1')
        print(yaml.dump(docs))




a = []
a.append({'role':'user'})
a.append({'role':'tryer'})
# b = []
# b.append({'role':'user'})
# b.append({'role':'tryer'})
# ff2(a, b)
ff1(a)

#!/usr/bin/env python3


# with open('actions.yaml') as f:

#     docs1 = yaml.load_all(f, Loader=yaml.FullLoader)

#     docs1 = list(docs1)
#     docs1[0]['actions'].append(docs[0][0])
#     docs1[0]['actions'].append(docs[0][1])
# with open('actions.yaml', 'w') as f:
#     yaml.dump(docs1, f)


