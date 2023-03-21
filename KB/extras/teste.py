###############################################################################
#                                                                             #
# Licensed under the Apache License, Version 2.0 (the "License"); you may     #
# not use this file except in compliance with the License. You may obtain a   #
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0           #
#                                                                             #
# Unless required by applicable law or agreed to in writing, software         #
# distributed under the License is distributed on an "AS IS" BASIS,           #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
# See the License for the specific language governing permissions and         #
# limitations under the License.                                              #
#                                                                             #
###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 16 Nov 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
# @last update:                                                               #  
#   version 1.1:                                                              #      
#   (author:  )                                                 # 
#                                                                             #   
###############################################################################
#
# This module create CORD-19 corpus dataset as <user, item, rating, item_name, year>.
# The items should be defined by user

# python3 create_cord19_recsys_dataset2.py   

# Metapub is a Python library that provides python

from configparser import Error
import os
import sys
from unittest import result
if os.path.isdir( "DiShIn" ):
    pass
sys.path.insert( 1, '/KB/src/DiShIn/sspmy/' )
import ssmpy
import pandas as pd
import numpy as np
from myconfiguration import MyConfiguration as cfg

from bioservices import ChEBI

from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs

# from scipy import stats

# from Utils.utils2ontologies import get_owl_path, get_db_path, loading_items, get_entities_labels
# from Utils.utils import upload_dataset, save_final_data
from Utils.utils2database import check_database, save_to_mysql, create_table, get_values

# import mysql.connector as connector
# from sqlalchemy import create_engine
# import pymysql
# ---------------------------------------------------------------------------------------- #

def update_onto(lexicon):
    '''
    Update ontologies
    '''
    print("Download latest obo files and process lexicons")
    
    if len(lexicon) == 0:
        lexicon = ["doid", "go", "hpo", "chebi"] 
    for l in lexicon:
        path_owl = get_owl_path(l)
        path_db = get_db_path(l)
        
        if os.path.isfile(path_db):
            print( f"Database ontology ``{l}.db'' file already exists" )
        else:
            ssmpy.create_semantic_base( path_owl, path_db,
                                "http://purl.obolibrary.org/obo/",
                                "http://www.w3.org/2000/01/rdf-schema#subClassOf", "" )

# ---------------------------------------------------------------------------------------- #

def merge_tables():
    table_name = 'similarity'
    cols_name1 = ["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc","sim_rel", "sim_jac", "sim_islch"]
    sim_df = pd.DataFrame((), columns=cols_name1)
    print(cols_name1[2:])
    
    tablename= 'norm_similarity_chebi'
    count=0
    for s in cols_name1[2:]:
        
        # ssmpy.semantic_base(get_db_path(onto))
        # create_table('_'.join([table_name,onto]))
        # data set contains <user, item, rating>
        
    #  ---------- GET ENTITIES LABELS OF THE 1st QUARTILE ---------- ## 
        if s=='sim_resnik':       
            sim_df = get_values('_'.join([tablename,s]),sim=s)
            sim_df[["comp_1", "comp_2"]] = sim_df[["comp_1", "comp_2"]].astype('int')

        else:
            new_df = get_values('_'.join([tablename,s]),s)
            new_df[["comp_1", "comp_2"]] = new_df[["comp_1", "comp_2"]].astype('int')
            sim_df=pd.merge(sim_df, new_df, on=["comp_1", "comp_2"])
        print(sim_df.head(10))
    create_table('_'.join([table_name,'chebi']))
    save_to_mysql( sim_df.drop_duplicates(), '_'.join([table_name,'chebi']), '' )

# ---------------------------------------------------------------------------------------- #


def get_molecule():

    item1 = ['CHEBI_15361']
    item2 = ['CHEBI_103229', 'CHEBI_150', 'CHEBI_17818', 'CHEBI_24156', \
    'CHEBI_34386', 'CHEBI_50934', 'CHEBI_51286', 'CHEBI_66106', 'CHEBI_8186', 'CHEBI_88',\
    'CHEBI_96062', 'CHEBI_10822'] 

    def tanimoto_calc(smi1, smi2):
        mol1 = Chem.MolFromSmiles(smi1)
        mol2 = Chem.MolFromSmiles(smi2)
        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 3, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 3, nBits=2048)
        s = round(DataStructs.TanimotoSimilarity(fp1,fp2),7)
        return s


    c = ChEBI()
    res = c.getCompleteEntity(item1[0].replace('_',':'))  
    print(getattr(c.getCompleteEntity(item1[0].replace('_',':')),'smiles', None))

    if getattr(c.getCompleteEntity(item1[0].replace('_',':')),'smiles', None):
       res = c.getCompleteEntity(item1[0].replace('_',':')) 
       i=0
       for it in item2:
            if getattr(c.getCompleteEntity(it.replace('_',':')),'smiles', None):
                i+=1
                res2=c.getCompleteEntity(it.replace('_',':'))
                print(f'{i} {tanimoto_calc(res.smiles,res2.smiles)}')
        
# ---------------------------------------------------------------------------------------- #

def main():
    
    # cols_name1 = ["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc","sim_rel", "sim_jac", "sim_islch"]
    # sim_df = pd.DataFrame((), columns=cols_name1)

    # tablename= 'norm_similarity_chebi'

    # for s in cols_name1.iloc[:,2:7]:
        
    #     # ssmpy.semantic_base(get_db_path(onto))
    #     # create_table('_'.join([table_name,onto]))
    #     # data set contains <user, item, rating>
        
    # #  ---------- GET ENTITIES LABELS OF THE 1st QUARTILE ---------- ## 
    #     if s=='sim_resnik':       
    #         sim_df = get_values('_'.join([tablename,cols_name1]),sim=s)
    #     else:
    #         new_df = get_values('_'.join([tablename,cols_name1]),s)
    #         sim_df[s]=new_df[sim_df['comp_1']==new_df['comp_1']&sim_df['comp_2']==new_df['comp_2']][s]
        
        
       
    #print(df.loc[~(df[cols[1:]]==0).all(axis=1),:])  

    """ threshold = 0.15
    is_chebi, is_do, is_go, is_hp = True, False, False, False

    path_to_metadata = '/ELT/data/results/comm_subset_cord-19_dataset_small.csv'
    path_cord_ds = '/ELT/data/results/comm_subset_cord-19_sim.csv'
    path_cord_ds1 = '/ELT/data/results/comm_subset_cord-19_sim_label.csv'
    table_name = 'similarity'

    lexicon = []
    if is_chebi:
        lexicon.append('chebi')
    if is_do:
        lexicon.append('doid')
    if is_go:    
        lexicon.append('go')
    if is_hp:
        lexicon.append('hpo') """

    ## updating ontologies  
    #update_onto(lexicon)
    
    # # ---------------------------------------------------------------------------------------- #
    # # connect to mysql table
    # check_database()
    
    # ## pd.DataFrame(columns=['comp_1', 'comp_2', 'sim_resnik', 'sim_lin', 'sim_jc', 'geom_mean', 'range', 'std'])
    # df = pd.DataFrame()
    # count=0
    # for onto in lexicon:
    #     print(onto)
    #     df_dataset = upload_dataset(path_to_metadata, onto.upper()+'_' )
    #     ssmpy.semantic_base(get_db_path(onto))
    #     print(df_dataset)
    #     for item in df_dataset['item']:
    #         count+=1
    #         print(f'{count}:  {item}')
    #         item_value = item.split('_')[1]
    #         ancestor = ssmpy.get_ancestors(int(item_value))
    #         if not ancestor:
    #             continue    
    # ## ---------- CALCULATE SEMANTIC SIMILARITY OF EACH ENTITY IN THE LIST ----------                  
    # #         for a in ancestor:
    # #             if ssmpy.ssm_resnik(item_value, str(a)) >= threshold:# and item_value != str(a): 
    # #                 pair = {'item1': item, 'item2': onto.upper()+'_'+str(a)} 
    # #                 df = df.append(pair, ignore_index=True)
    # #             if ssmpy.ssm_jiang_conrath(item_value, str(a)) >= threshold:# and item_value != str(a):
    # #                 pair = {'item1': item, 'item2': onto.upper()+'_'+str(a)} 
    # #                 df = df.append(pair, ignore_index=True)
    # #             if ssmpy.ssm_lin(item_value, str(a)) >= threshold:# and item_value != str(a):
    # #                 pair = {'item1': item, 'item2': onto.upper()+'_'+str(a)} 
    # #                 df = df.append(pair, ignore_index=True)  
    # ## ---------- END OF CALCULATE SEMANTIC SIMILARITY OF EACH ENTITY IN THE LIST ----------   
    # #  
    #         # # join all entities with his ancestors, and after only select the 15% with higher semantic similarity
    #         conn = ssmpy.create_connection(get_db_path(onto))
    #         # create a list of ancestor
    #         ancestor_ids = [onto.upper()+'_' + str(s) for s in ancestor] 
    #         #df["comp_2"] = ancestor_ids.map(df.set_index('comp_1')).fillna(0) 
    #         ## calculate semantic similarity: resnik, jiang and conrath and lin
    #         results = ssmpy.light_similarity(conn, [item], ancestor_ids, 'all', 20)
    #         results = [item for items in results for item in items]
    #         sim_df = pd.DataFrame( results, columns=["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc"] )
    #         ## remove rows where entities are equal (avoid sim = 1)
    #         sim_df = sim_df[sim_df['comp_1'] != sim_df['comp_2']]
    #         print(sim_df)

    #         ##  ---------- CALCULATE GEOMETRIC MEAN, RANGE (MAX-MIN), STD  ---------- ##
    #         # calculate geometric mean, first remove zeros if exist
    #         sims = ["sim_resnik", "sim_lin", "sim_jc"]
    #         sim_df = sim_df[~np.any(sim_df[sims].applymap(np.int64) == 0, axis=1)]
    #         sim_df['geom_mean'] = None
    #         sim_df['geom_mean'] = stats.gmean(sim_df.iloc[:, 2:4], axis = 1)            
    #         sim_df['span'] = None
    #         sim_df['span'] = sim_df.iloc[:, 2:4].max(axis=1) - sim_df.iloc[:, 2:4].min(axis=1)
    #         sim_df['std'] = None
    #         sim_df['std'] = sim_df.iloc[:, 2:4].std(axis=1)
    #         #print(sim_df)
    #         df = df.append(sim_df, ignore_index=True)            
            
    #         # # # ##  ---------- SAVE ALL IN DB FOR EACH 1000 ROWS ---------- ##
    #         # # # if count>3:
    #         # # #     df_similar = df.drop_duplicates()
    #         # # #     print(df_similar)
    #         # # #     # creation of engine to MYSQL database to insert pandas DataFrame in the database
    #         # # #     save_to_mysql( df_similar, table_name, onto.upper()+'_' )
    #         # # #     df = pd.DataFrame()
    #         # # #     count = 0
    #         # # #     # close connection
    #         # # #     conn.close()
    #         # # #     break
    #         # # # ##  ---------- END OF SAVE ALL IN DB FOR EACH 1000 ROWS ---------- ##
    #         if count>2:
    #             break

    ##  ---------- GET ENTITIES LABELS OF THE 15% BEST VALUES ---------- ## 
    """  onto='chebi'
    # --- example
    df_dataset = pd.DataFrame(np.array([[0,'CHEBI_15361', 1, 2021], [0,'CHEBI_15378', 1, 2021], [0,'CHEBI_15362', 1, 2021], \
        [17,'CHEBI_15361', 1, 2021], [52,'CHEBI_15361', 1, 2021], [67,'CHEBI_15361', 1, 2021]]), columns=['user', 'item', 'rating','year'])
    #
    # item1 = 'CHEBI_15361'
    # item2 = ['CHEBI_103229', 'CHEBI_150', 'CHEBI_17818', 'CHEBI_24156', \
    #     'CHEBI_34386', 'CHEBI_50934', 'CHEBI_51286', 'CHEBI_66106', 'CHEBI_8186', 'CHEBI_88',\
    #     'CHEBI_96062'] 
    # --- end of example
    df_similar = get('similarity_chebi')

    df_similar.comp_1 = onto.upper()+'_'+df_similar.comp_1.map(str)
    df_similar.comp_2 = onto.upper()+'_'+df_similar.comp_2.map(str)

    print(df_similar)
    ## find index where item1 exist in dataframe
    for item1 in df_dataset['item'].drop_duplicates().values.tolist():
        
        idx = df_dataset.index[df_dataset['item']==''.join(item1)].tolist()
        # get item2 list 
        item2=df_similar[df_similar['comp_1']==''.join(item1)]['comp_2']
        
        # replicate for each user the item2 where similarity semantic between items are higher
        pair = [{'user':df_dataset['user'].iloc[i],'item':c,'rating':df_dataset['rating'].iloc[i],'year':df_dataset['year'].iloc[i]} for i in idx for c in item2 ]
        # append values from orginal dataframe and sort by user
        df_dataset = df_dataset.append(pair, ignore_index=True).sort_values(by=['user']).reset_index(drop=True)  
    print(df_dataset) """

    # ## ---------- get entities labels ----------
    # list_of_entities = df_dataset.item.unique()
    # #print(list_of_entities) 

    # # loading ontologies   
    # chebi, do, go, hp = loading_items(is_chebi, is_do, is_go, is_hp)

    # entities_label = get_entities_labels(list_of_entities, chebi, do, go, hp)
    # print(entities_label)
    # df_entities = pd.DataFrame(list_of_entities, columns=["item_id"])
    # df_entities["entity_name"] = np.array(entities_label)

    # print('mapping labels')
    # df_dataset["item_name"] = df_dataset["item"].map(df_entities.set_index('item_id')["entity_name"]).fillna(0)
    
    # # print('saving data')
    # # save_final_data(data=df_dataset[['user', 'item', 'rating', 'item_name', 'year']], \
    # #     path=path_to_cord_ds)

    # print(df_dataset)
# ---------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()