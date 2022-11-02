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

# python3 create_cord19_recsys_ds_kb.py   

# Metapub is a Python library that provides python

import os
import random
import sys
from tracemalloc import stop

import ssmpy 
from DiShIn.ssmpy import new_light_similarity
import pandas as pd
import numpy as np
from datetime import datetime
if os.path.isdir( "DiShIn" ):
    pass
sys.path.insert( 1, '/KB/src/DiShIn/sspmy/' )
import sqlite3
from scipy import stats
from bioservices import ChEBI

from myconfiguration import MyConfiguration as cfg

from Utils.utils2ontologies import get_owl_path, get_db_path, loading_items, get_primary_ids
from Utils.utils import upload_dataset,  save_metadata
from Utils.utils2database import check_database, create_table, save_to_mysql,get_values

pd.set_option('display.max_columns', None)
pd.set_option("max_rows", None)
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs


def tanimoto_calc(smi1, smi2):
    mol1 = Chem.MolFromSmiles(smi1)
    mol2 = Chem.MolFromSmiles(smi2)
    fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 3, nBits=2048)
    fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 3, nBits=2048)
    s = round(DataStructs.TanimotoSimilarity(fp1,fp2),7)
    return s

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

def update_onto(lexicon):
    '''
    Update ontologies
    '''
    print("Download latest obo files and process lexicons")
    
    if len(lexicon) == 0:
        lexicon = ["doid", "go", "hpo", "chebi"] 
    for l in lexicon:
        print(l)
        path_owl = get_owl_path(l)
        path_db = get_db_path(l)
        
        if os.path.isfile(path_db):
            print( f"Database ontology ``{l}.db'' file already exists" )
        else:
            ssmpy.create_semantic_base( path_owl, path_db,
                                "http://purl.obolibrary.org/obo/",
                                "http://www.w3.org/2000/01/rdf-schema#subClassOf", "" )
   

def drop_duplicate_author(df,drop_col):
    '''
    Rewrite the dataframe where the author who writes about an entity is removed 
    regardless of the year of publication. To the 'rating' column are added all 
    the entries of that entity 
    parameter df:: dataframe
              drop_col: columns name to remove
    return:: dataframe
    '''
    ## remove 'year' information from dataset
    df = df.drop(drop_col,axis=1)
    ## get the first identifier if there are multiple entries for the same author
    df_ids = df[['user','user_name']]
    ids = df_ids.drop_duplicates(subset = ['user_name'],keep='first')
    ## change value type of 'rating' column to get the sum
    df["rating"] = pd.to_numeric(df["rating"])
    df=df.groupby(['user_name','item','item_name'])['rating'].sum().reset_index()
    ## adding user id from each author name
    df["user"] = df["user_name"].map(ids.set_index('user_name')["user"]).fillna(0)
    
    cols = list(df.columns)
    cols = [cols[-1]] + cols[:-1]
    df = df[cols]
    return df       

# ---------------------------------------------------------------------------------------- #

TESTE = np.array([[1,'A Kopitar-Jerala Nata','CHEBI_132943','aspartate',1,2012],\
[1,'A Kopitar-Jerala Nata','CHEBI_15356','cysteine',1,2012],\
[1,'A Kopitar-Jerala Nata','CHEBI_15841','polypeptide',1,2012],\
[1,'A Kopitar-Jerala Nata','CHEBI_16113','cholesterol',1,2012],\
[33,'A Kopitar-Jerala Nata','CHEBI_132943','aspartate',1,2014],\
[33,'A Kopitar-Jerala Nata','CHEBI_25016','lead atom',1,2014],\
[174032,'yang Hui','CHEBI_24433','group',1,2020],\
[174032,'yang Hui','CHEBI_25016','lead atom',1,2020],\
[174032,'yang Hui','CHEBI_132943','aspartate',1,2020]])

def df_column_switch(df, column1, column2):
    i = list(df.columns)
    a, b = i.index(column1), i.index(column2)
    i[b], i[a] = i[a], i[b]
    df = df[i]
    return df
    
def main():

    df = pd.DataFrame(TESTE,columns=('user','user_name','item','item_name','rating','year'))
    
    df = drop_duplicate_author(df,drop_col = ['year'])
    print(df)


    import time
    arg = cfg.getInstance()
   
    is_chebi, is_do, is_go, is_hp = False, False, False, False

    path_to_ds = arg.path_to_ds

    active_lexicons = arg.item_prefix.replace(' ', '').split(',')
    for item in active_lexicons:
        if item.startswith('chebi'):
            is_chebi = True
        if item.startswith('doid'):
            is_do = True
        if item.startswith('go'):
            is_go = True
        if item.startswith('hp'):
            is_hp = True         
    
    # item1 = ['CHEBI_15361']
    # item2 = ['CHEBI_103229', 'CHEBI_150', 'CHEBI_17818', 'CHEBI_24156', \
    # 'CHEBI_34386', 'CHEBI_50934', 'CHEBI_51286', 'CHEBI_66106', 'CHEBI_8186', 'CHEBI_88',\
    # 'CHEBI_96062', 'CHEBI_10822'] 

    c = ChEBI()
    # res = c.getCompleteEntity(item1[0].replace('_',':'))  
    # print(getattr(c.getCompleteEntity(item1[0].replace('_',':')),'smiles', None))

    # if getattr(c.getCompleteEntity(item1[0].replace('_',':')),'smiles', None):
    #    res = c.getCompleteEntity(item1[0].replace('_',':')) 
    #    i=0
    #    for it in item2:
    #         if getattr(c.getCompleteEntity(it.replace('_',':')),'smiles', None):
    #             i+=1
    #             res2=c.getCompleteEntity(it.replace('_',':'))
    #             print(f'{i} {tanimoto_calc(res.smiles,res2.smiles)}')
        
    cols_name1 = ["comp_1", "comp_2", "sim_resnik"]
    sim_df = pd.DataFrame((), columns=cols_name1)

    tablename= 'similarity_chebi'
    table_name='similarity_structural'
    onto = 'CHEBI'
    count=0
    create_table('_'.join([table_name,onto]))

    for s in cols_name1[2:]:
        
    #  ---------- GET ENTITIES LABELS OF THE 1st QUARTILE ---------- ## 
        if s=='sim_resnik':       
            sim_df = get_values(tablename,sim=s)
            sim_df[["comp_1", "comp_2"]] = sim_df[["comp_1", "comp_2"]].astype('int')
            #new_df = sim_df.iloc[:,:2]
            #new_df['sim_tanimoto'] = 0
            new_df=pd.DataFrame()
            for i in range(sim_df.shape[0]):
                str1= 'CHEBI:'+str(sim_df['comp_1'].values[i])
                str2= 'CHEBI:'+str(sim_df['comp_2'].values[i])
                if getattr(c.getCompleteEntity(str1),'smiles', None):
                    res = c.getCompleteEntity(str1) 
                    #print(res.smiles)
                    if getattr(c.getCompleteEntity(str2),'smiles', None):
                        res2=c.getCompleteEntity(str2)
                        #print(res2.smiles)
                        #print(f'{i} {tanimoto_calc(res.smiles,res2.smiles)}')
                        pair = [{'comp_1':int(sim_df.at[i,'comp_1']),'comp_2':int(sim_df.at[i,'comp_2']),'sim_tanimoto':tanimoto_calc(res.smiles,res2.smiles)}]
                        #print(pair)
                        # append values from orginal dataframe and sort by user
                        new_df = new_df.append(pair, ignore_index=True).reset_index(drop=True)  
                        count+=1
            
                        if count>499: #count>499:
                            # creation of engine to MYSQL database to insert pandas DataFrame in the database
                            save_to_mysql( new_df.drop_duplicates(), '_'.join([table_name,onto]),None)
                            # reset all values
                            print("***** SAVE IN MYSQL ********")
                            new_df = pd.DataFrame()
                            count = 0
            if not new_df.empty:
                # creation of engine to MYSQL database to insert pandas DataFrame in the database
                save_to_mysql( new_df.drop_duplicates(), '_'.join([table_name,onto]), None) 
                # reset all values
                new_df = pd.DataFrame()
                count = 0               
                # if count>5:
                #     break
        #print(new_df.head(10))
            
            
        

    #print(c.search_molecule('aspirin'))
    #for it in item2:
    #    print(tanimoto_calc(item1,it))


    # ## updating ontologies  
    #update_onto(active_lexicons)
    
    # loading ontologies   
    #chebi, do, go, hp = loading_items(is_chebi, is_do, is_go, is_hp)
    
    # ---------------------------------------------------------------------------------------- #
    # connect to mysql table
    #check_database()
    
    

       
    # # pd.DataFrame(columns=['comp_1', 'comp_2', 'sim_resnik', 'sim_lin', 'sim_jc', 'geom_mean', 'span', 'std'])
    # df = pd.DataFrame()
    # count, count_item = 0, 0

    # for onto in active_lexicons:
    #     print(onto)
    #     ssmpy.semantic_base(get_db_path(onto))
    #     create_table('_'.join([table_name,onto]))
    #     # data set contains <user, item, rating>
    #     df_dataset = upload_dataset(path_to_ds, onto.upper()+'_' )
    #     # print(df_dataset)
    #     list_of_entities = df_dataset.item.unique()
    #     list_of_entities = np.random.choice(list_of_entities,10)

    #     for item in list_of_entities:            
    #         count+=1
    #         count_item+=1
    #         print(f'{count_item}:  {item}')
    #         item_value = item.split('_')[1]
    #         ancestor = ssmpy.get_ancestors(int(item_value))
    #         if not ancestor:
    #             continue 
               
    #         # create a list of ancestor
    #         ancestor_ids = [onto.upper()+'_' + str(s) for s in ancestor] 
    #         # get primary id of the CHEBI entity
    #         if item.startswith('CHEBI'):
    #             ancestor_ids = get_primary_ids(ancestor_ids, chebi)
                
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
    #         # if count>1:
    #         #     break
    #         # # join all entities with his ancestors, and after only select the 15% with higher semantic similarity
    #         conn = ssmpy.create_connection(get_db_path(onto))
    #         #df["comp_2"] = ancestor_ids.map(df.set_index('comp_1')).fillna(0) 
            
    #         ## calculate semantic similarity: resnik, jiang and conrath and lin
    #         # results = ssmpy.light_similarity(conn, [item], ancestor_ids, 'lin', 20)
    #         # results = [item for items in results for item in items]
    #         # sim_df = pd.DataFrame( results, columns=["comp_1", "comp_2", "sim_lin"] )
            
    #         ## ------------------------------- ALL ------------------------------ ##
    #         ## OLDER            
    #         results1 = ssmpy.light_similarity(conn, [item], ancestor_ids, 'all', 20)
    #         results1 = [item for items in results1 for item in items]
    #         ## NEWER 
    #         results2 = new_light_similarity(conn, [item], ancestor_ids, 'all', 20)
    #         results2 = [item for items in results2 for item in items]

    #     #     ### ************* NEW  *************** ###   
    #         cols_name1 = ["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc"]
    #         sim_df1 = pd.DataFrame(results1, columns=cols_name1)
    #         cols_name1 = ["comp_1", "comp_2", "sim_rel", "sim_jac", "sim_islch"]
    #         sim_df2 = pd.DataFrame(results2, columns=cols_name1)
    #         sim_df = sim_df1.merge(sim_df2,on=['comp_1','comp_2'])


    #         ##  ---------- CALCULATE GEOMETRIC MEAN, RANGE (MAX-MIN), STD  ---------- ##
    #         # calculate geometric mean, first remove zeros if exist
    #         """ sims = ["sim_resnik", "sim_lin", "sim_jc"]
    #         sim_df = sim_df[~np.any(sim_df[sims].applymap(np.int64) == 0, axis=1)]
    #         sim_df['geom_mean'] = None
    #         sim_df['geom_mean'] = stats.gmean(sim_df.iloc[:, 2:4], axis = 1)            
    #         sim_df['span'] = None
    #         sim_df['span'] = sim_df.iloc[:, 2:4].max(axis=1) - sim_df.iloc[:, 2:4].min(axis=1)
    #         sim_df['std'] = None
    #         sim_df['std'] = sim_df.iloc[:, 2:4].std(axis=1) """

    #         ## remove rows where entities are equal (avoid sim = 1)
    #         sim_df = sim_df[sim_df['comp_1'] != sim_df['comp_2']]
    #         ## drop rows where similarities are zeros
    #         cols_name = ["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc", "sim_rel", "sim_jac", "sim_islch"]
    #         sim_df = sim_df.loc[~(sim_df[cols_name[2:]]==0).all(axis=1),:]

    #         #print(sim_df)
    #         df = df.append(sim_df, ignore_index=True)            
    #         #check if the table end
    #         ##  ---------- SAVE ALL IN DB FOR EACH 500 ROWS ---------- ##
    #         if count>40: #count>499:
    #             # creation of engine to MYSQL database to insert pandas DataFrame in the database
    #             save_to_mysql( df.drop_duplicates(), '_'.join([table_name,onto]), onto.upper()+'_' )
    #             # reset all values
    #             print("***** SAVE IN MYSQL ********")
    #             df = pd.DataFrame()
    #             sim_df = pd.DataFrame()
    #             count = 0
    #             # close connection
    #             conn.close()
            
    #         # if count>1:
    #         #     break
    #     if not df.empty:
    #         # creation of engine to MYSQL database to insert pandas DataFrame in the database
    #         save_to_mysql( df.drop_duplicates(), '_'.join([table_name,onto]), onto.upper()+'_' ) 
    #         # reset all values
    #         df = pd.DataFrame()
    #         sim_df = pd.DataFrame()
    #         count = 0
    #         # close connection
    #         conn.close()          
    #         #  ---------- END OF SAVE ALL IN DB FOR EACH 500 ROWS ---------- ##
   
# ---------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()