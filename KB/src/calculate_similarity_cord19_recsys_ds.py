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
# This module calculates the similarity between entities and save the results in
# a mysql table. The entities exist on the CORD-19 dataset corpus. Moreover, we 
# add their ancestors to improve resullts
#
# For the CHEBI ontology and if we want to consider the structural similarity,
# we must to include calculate_structural_sim() method in main

# python3 calculate_similarity_cord19_recsys_ds.py   

# Metapub is a Python library that provides python

import os
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
from myconfiguration import MyConfiguration as cfg

from Utils.utils2ontologies import get_owl_path, get_db_path, loading_items, get_primary_ids
from Utils.utils import upload_dataset, save_metadata
from Utils.utils2database import check_database, create_table, save_to_mysql, get_values,\
    create_table_str

from bioservices import ChEBI
from rdkit import Chem
from rdkit.Chem import AllChem
from rdkit import DataStructs

pd.set_option('display.max_columns', None)
pd.set_option("max_rows", None)

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
            print('here')
            ssmpy.create_semantic_base( path_owl, path_db,
                                "http://purl.obolibrary.org/obo/",
                                "http://www.w3.org/2000/01/rdf-schema#subClassOf", "" )

# ---------------------------------------------------------------------------------------- #

def calculate_structural_sim(table):
    '''
    Calculate structural similarity, only for CHEBI ontology, and save the results in a
    novel table.
    :param table: name of the previous table. Assume that we have a table with other
    methods
    '''

    def tanimoto_calc(smi1, smi2):
        mol1 = Chem.MolFromSmiles(smi1)
        mol2 = Chem.MolFromSmiles(smi2)
        fp1 = AllChem.GetMorganFingerprintAsBitVect(mol1, 3, nBits=2048)
        fp2 = AllChem.GetMorganFingerprintAsBitVect(mol2, 3, nBits=2048)
        s = round(DataStructs.TanimotoSimilarity(fp1,fp2),7)
        return s

    # get entities from previous created table
    # 
    sim_df = get_values(table,sim='sim_resnik')
    sim_df[["comp_1", "comp_2"]] = sim_df[["comp_1", "comp_2"]].astype('int') 

    c = ChEBI()
   
    table_name='similarity_structural'
    onto = 'chebi'
    #create a new table with structural similarity values
    create_table_str('_'.join([table_name,onto]))

    df = pd.DataFrame()
    count = 0
    for i in range(sim_df.shape[0]):
        str1= onto.upper()+':'+str(sim_df['comp_1'].values[i])
        str2= onto.upper()+':'+str(sim_df['comp_2'].values[i])
        if getattr(c.getCompleteEntity(str1),'smiles', None):
            res = c.getCompleteEntity(str1) 
            #print(res.smiles)
            if getattr(c.getCompleteEntity(str2),'smiles', None):
                res2=c.getCompleteEntity(str2)
                #print(f'{i} {tanimoto_calc(res.smiles,res2.smiles)}')
                pair = [{'comp_1':int(sim_df.at[i,'comp_1']),'comp_2':int(sim_df.at[i,'comp_2']),'sim_tanimoto':tanimoto_calc(res.smiles,res2.smiles)}]
                #print(pair)
                # append values from orginal dataframe
                df = df.append(pair, ignore_index=True).reset_index(drop=True)  
                count+=1
    
                if count>499: #count>499:
                    # creation of engine to MYSQL database to insert pandas DataFrame in the database
                    save_to_mysql( df.drop_duplicates(), '_'.join([table_name,onto]),None)
                    # reset all values
                    print("***** SAVE IN MYSQL ********")
                    df = pd.DataFrame()
                    count = 0
    if not df.empty:
        # creation of engine to MYSQL database to insert pandas DataFrame in the database
        save_to_mysql( df.drop_duplicates(), '_'.join([table_name,onto]), None) 
        # reset all values
        df = pd.DataFrame()
        count = 0   

# ---------------------------------------------------------------------------------------- #

def main():

    import time
    start_time = datetime.now()
    arg = cfg.getInstance()
   
    is_chebi, is_do, is_go, is_hp = False, False, False, False

    path_to_ds = arg.path_to_ds #'/ELT/data/results/comm_subset_cord-19_dataset_small.csv'

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
    
    # ## updating ontologies  
    update_onto(active_lexicons)
    
    # loading ontologies   
    chebi, do, go, hp = loading_items(is_chebi, is_do, is_go, is_hp)
    
    # ---------------------------------------------------------------------------------------- #
    # connect to mysql table
    check_database()
    
    table_name = arg.tablename
    df = pd.DataFrame()
    count, count_item = 0, 0

    for onto in active_lexicons:
        print(onto)
        ssmpy.semantic_base(get_db_path(onto))
        create_table('_'.join([table_name,onto]))
        # data set contains <user, item, rating>
        df_dataset = upload_dataset(path_to_ds, onto.upper()+'_' )
        # print(df_dataset)
        list_of_entities = df_dataset.item.unique()

        for item in list_of_entities:            
            count+=1
            count_item+=1
            print(f'{count_item}:  {item}')
            item_value = item.split('_')[1]
            ancestor = ssmpy.get_ancestors(int(item_value))
            if not ancestor:
                continue 
               
            # create a list of ancestor
            ancestor_ids = [onto.upper()+'_' + str(s) for s in ancestor] 
            # get primary id of the CHEBI entity
            if item.startswith('CHEBI'):
                ancestor_ids = get_primary_ids(ancestor_ids, chebi)
                
    ## ---------- CALCULATE SEMANTIC SIMILARITY OF EACH ENTITY IN THE LIST ----------                  
    #         for a in ancestor:
    #             if ssmpy.ssm_resnik(item_value, str(a)) >= threshold:# and item_value != str(a): 
    #                 pair = {'item1': item, 'item2': onto.upper()+'_'+str(a)} 
    #                 df = df.append(pair, ignore_index=True)
    #             if ssmpy.ssm_jiang_conrath(item_value, str(a)) >= threshold:# and item_value != str(a):
    #                 pair = {'item1': item, 'item2': onto.upper()+'_'+str(a)} 
    #                 df = df.append(pair, ignore_index=True)
    #             if ssmpy.ssm_lin(item_value, str(a)) >= threshold:# and item_value != str(a):
    #                 pair = {'item1': item, 'item2': onto.upper()+'_'+str(a)} 
    #                 df = df.append(pair, ignore_index=True)  
    ## ---------- END OF CALCULATE SEMANTIC SIMILARITY OF EACH ENTITY IN THE LIST ----------   
    #  
            # if count>1:
            #     break
            # # join all entities with his ancestors, and after only select the 15% with higher semantic similarity
            conn = ssmpy.create_connection(get_db_path(onto))
            #df["comp_2"] = ancestor_ids.map(df.set_index('comp_1')).fillna(0) 
            
            ## calculate semantic similarity: resnik, jiang and conrath and lin
            # results = ssmpy.light_similarity(conn, [item], ancestor_ids, 'lin', 20)
            # results = [item for items in results for item in items]
            # sim_df = pd.DataFrame( results, columns=["comp_1", "comp_2", "sim_lin"] )
            
            ## ------------------------------- ALL ------------------------------ ##
            ## OLDER            
            results1 = ssmpy.light_similarity(conn, [item], ancestor_ids, 'all', 20)
            results1 = [item for items in results1 for item in items]
            ## NEWER 
            results2 = new_light_similarity(conn, [item], ancestor_ids, 'all', 20)
            results2 = [item for items in results2 for item in items]

        #     ### ************* NEW  *************** ###   
            cols_name1 = ["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc"]
            sim_df1 = pd.DataFrame(results1, columns=cols_name1)
            cols_name1 = ["comp_1", "comp_2", "sim_rel", "sim_jac", "sim_islch"]
            sim_df2 = pd.DataFrame(results2, columns=cols_name1)
            sim_df = sim_df1.merge(sim_df2,on=['comp_1','comp_2'])


            ##  ---------- CALCULATE GEOMETRIC MEAN, RANGE (MAX-MIN), STD  ---------- ##
            # calculate geometric mean, first remove zeros if exist
            """ sims = ["sim_resnik", "sim_lin", "sim_jc"]
            sim_df = sim_df[~np.any(sim_df[sims].applymap(np.int64) == 0, axis=1)]
            sim_df['geom_mean'] = None
            sim_df['geom_mean'] = stats.gmean(sim_df.iloc[:, 2:4], axis = 1)            
            sim_df['span'] = None
            sim_df['span'] = sim_df.iloc[:, 2:4].max(axis=1) - sim_df.iloc[:, 2:4].min(axis=1)
            sim_df['std'] = None
            sim_df['std'] = sim_df.iloc[:, 2:4].std(axis=1) """

            ## remove rows where entities are equal (avoid sim = 1)
            sim_df = sim_df[sim_df['comp_1'] != sim_df['comp_2']]
            ## drop rows where similarities are zeros
            cols_name = ["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc", "sim_rel", "sim_jac", "sim_islch"]
            sim_df = sim_df.loc[~(sim_df[cols_name[2:]]==0).all(axis=1),:]

            #print(sim_df)
            df = df.append(sim_df, ignore_index=True)            
            #check if the table end
            ##  ---------- SAVE ALL IN DB FOR EACH 500 ROWS ---------- ##
            if count>499:
                # creation of engine to MYSQL database to insert pandas DataFrame in the database
                save_to_mysql( df.drop_duplicates(), '_'.join([table_name,onto]), onto.upper()+'_' )
                # reset all values
                print("***** SAVE IN MYSQL ********")
                df = pd.DataFrame()
                sim_df = pd.DataFrame()
                count = 0
                # close connection
                conn.close()
            
            # if count>1:
            #     break
        if not df.empty:
            # creation of engine to MYSQL database to insert pandas DataFrame in the database
            save_to_mysql( df.drop_duplicates(), '_'.join([table_name,onto]), onto.upper()+'_' ) 
            # reset all values
            df = pd.DataFrame()
            sim_df = pd.DataFrame()
            count = 0
            # close connection
            conn.close()          
            #  ---------- END OF SAVE ALL IN DB FOR EACH 500 ROWS ---------- ##
        time.sleep(.5)

    if is_chebi:    
        calculate_structural_sim(table_name)    
    # ---------------------------------------------------------------------------------------- #
   
    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\t No. entities: {count_item}\n\
                Results: { arg.path_to_ds_kb , path_to_ds }\n\
                '
    save_metadata(arg.path_to_info, metadata) 
    print("FINISHED!")

# ---------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()