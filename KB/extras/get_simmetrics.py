import ssmpy
import pandas as pd
import numpy as np
#import sys, os
#sys.path.insert(1,'/KB/src/utils/')
from Utils.utils2ontologies import get_owl_path, get_db_path, loading_items
import rdflib
from rdflib import URIRef
from bioservices import ChEBI


# --------------------------------------------------------------------------- #

def get_owl_path(entity):
    if entity == 'doid':
        return '/data/ontologies/doid.owl'
    elif entity == 'chebi':
        return '/data/ontologies/chebi_lite.owl'   
    return ''

# --------------------------------------------------------------------------- #

def get_db_path(entity):
    if entity == 'doid':
        return '/data/ontologies/doid.db'
    elif entity == 'chebi':
        return '/data/ontologies/chebi_lite.db'
    return ''

# --------------------------------------------------------------------------- #

def check_primary_ids(lst, prefix_chebi):
    '''
    Get entities ids from http://purl.obolibrary.org/obo/ based on items prefix
    :param  lst: list of entities
            chebi: items prefix of entities
    :return label: primary id
    '''
    ids = []
    for id in lst: 
        uri = URIRef('http://purl.obolibrary.org/obo/' + id)
        lab = prefix_chebi.label(uri)
        if not lab:
            ch = ChEBI()
            res = ch.getCompleteEntity(id.replace('_',':'))
            id = res.chebiId.replace(':','_')
        
        ids.append(id)       
    return ids

# --------------------------------------------------------------------------- #

item1 = ['CHEBI_15361']
item2 = ['CHEBI_103229', 'CHEBI_150', 'CHEBI_17818', 'CHEBI_24156', \
    'CHEBI_34386', 'CHEBI_50934', 'CHEBI_51286', 'CHEBI_66106', 'CHEBI_8186', 'CHEBI_88',\
    'CHEBI_96062', 'CHEBI_10822'] 

is_chebi, is_do, is_go, is_hp = True, False, False, False

chebi, do, go, hp = loading_items(is_chebi, is_do, is_go, is_hp)

primary, label = check_primary_ids(item2, 'CHEBI')
print (item2, 'primary id: ', primary)
print('labels: ', label)

ancestor_ids = ['CHEBI_15546', 'CHEBI_10822']

ssmpy.semantic_base('/data/ontologies/chebi_lite.db')#get_db_path('chebi'))
# print(df_dataset)
item1 = ['CHEBI_15361']
count=0
for item in item1:
    count+=1
    print(f'{count}:  {item}')
    item_value = item.split('_')[1]
    ancestor = ssmpy.get_ancestors(int(item_value))
    print(ancestor)
    conn = ssmpy.create_connection(get_db_path('chebi'))
    # create a list of ancestor
    #ancestor_ids = ['chebi'.upper()+'_' + str(s) for s in ancestor] 
    ancestor_ids = ['CHEBI_15546', 'CHEBI_10822']
    #df["comp_2"] = ancestor_ids.map(df.set_index('comp_1')).fillna(0) 
    ## calculate semantic similarity: resnik, jiang and conrath and lin
    results = ssmpy.light_similarity(conn, [item], ancestor_ids, 'all', 20)
    results = [item for items in results for item in items]
    sim_df = pd.DataFrame( results, columns=["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc"] )
    ## remove rows where entities are equal (avoid sim = 1)
    sim_df = sim_df[sim_df['comp_1'] != sim_df['comp_2']]
    print(sim_df)

e1='15361'
e2='10822'
print(e1, ' + ' , e2)
ssmpy.semantic_base("/data/ontologies/chebi_lite.db")
print('resnik: ', ssmpy.ssm_resnik(e1,e2))
print('lin: ', ssmpy.ssm_lin(e1,e2))
print('jiang: ',ssmpy.ssm_jiang_conrath(e1,e2))
e2='15546'
print(e1, ' + ' , e2)
ssmpy.semantic_base("/data/ontologies/chebi_lite.db")
print('resnik: ', ssmpy.ssm_resnik(e1,e2))
print('lin: ', ssmpy.ssm_lin(e1,e2))
print('jiang: ',ssmpy.ssm_jiang_conrath(e1,e2))
e2='26318'
ssmpy.semantic_base("/data/ontologies/chebi_lite.db")
print('resnik: ', ssmpy.ssm_resnik(e1,e2))
print('lin: ', ssmpy.ssm_lin(e1,e2))
print('jiang: ',ssmpy.ssm_jiang_conrath(e1,e2))


#ancestor_ids = ['CHEBI_15546', 'CHEBI_10822', 'CHEBI_144', 'CHEBI_10822', 'CHEBI_26318']
    
# root@199a3182dc84:/KB/extras# python3 get_simmetrics.py 
# 1:  CHEBI_15361
# [15361, 10822, 2968, 156, 4650, 1086, 150, 20990, 62506, 8351, 98521, 334, 69553, 3384, 18748, 546, 8352, 60724, 78304, 42428, 32, 69592, 2533, 2534, 55958, 164218]
#          comp_1        comp_2  sim_resnik   sim_lin    sim_jc
# 0   CHEBI_15361     CHEBI_150    1.139823  0.101486  0.047208
# 2   CHEBI_15361  CHEBI_164218    0.434088  0.038650  0.044259
# 3   CHEBI_15361    CHEBI_2533    1.139823  0.101486  0.047208
# 4   CHEBI_15361    CHEBI_2534    1.139823  0.101486  0.047208
# 5   CHEBI_15361    CHEBI_2968    0.434088  0.038650  0.044259
# 6   CHEBI_15361      CHEBI_32    0.361682  0.032203  0.043977
# 7   CHEBI_15361    CHEBI_3384    0.361682  0.032203  0.043977
# 8   CHEBI_15361    CHEBI_4650    0.074502  0.006633  0.042893
# 9   CHEBI_15361   CHEBI_60724    1.139823  0.103351  0.048129
# 10  CHEBI_15361   CHEBI_62506    0.434088  0.039360  0.045067
# 11  CHEBI_15361   CHEBI_69553    0.434088  0.038650  0.044259
# 12  CHEBI_15361   CHEBI_69592    0.361682  0.032203  0.043977
# 13  CHEBI_15361   CHEBI_78304    1.139823  0.101486  0.047208
# 14  CHEBI_15361    CHEBI_8351    1.139823  0.101486  0.047208
# 15  CHEBI_15361    CHEBI_8352    0.434088  0.038650  0.044259
# 16  CHEBI_15361   CHEBI_98521    0.434088  0.038650  0.044259
# 15361  +  10822
# resnik:  2.3408373161622213
# lin:  0.2289575275532447
# jiang:  0.0596441208400786
# 15361  +  15546
# resnik:  0
# Traceback (most recent call last):
#   File "get_simmetrics.py", line 64, in <module>
#     print('lin: ', ssmpy.ssm_lin(e1,e2))
#   File "/usr/local/lib/python3.6/dist-packages/ssmpy/ssm.py", line 568, in ssm_lin
#     aux = information_content(entry1) + information_content(entry2)
#   File "/usr/local/lib/python3.6/dist-packages/ssmpy/ssm.py", line 355, in information_content
#     return information_content_extrinsic(entry)
#   File "/usr/local/lib/python3.6/dist-packages/ssmpy/ssm.py", line 270, in information_content_extrinsic
#     freq = rows.fetchone()[0] + 1.0
# TypeError: 'NoneType' object is not subscriptable