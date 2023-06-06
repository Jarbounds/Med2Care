###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 16 Nov 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
# @last update:                                                               #  
#   version 1.1: 15 Feb 2023 add structural similarities: tanimoto & morgan   #      
#   (author: Matilde Pato)                                                    #
#   version 1.2: 21 Feb 2023 change pd.append() by pd.concat()                #      
#   (author: Matilde Pato)                                                    # 
#   version 1.3: 23 Feb 2023 structural similarity is removed and create a    #
#   new script to calculate them: calculate_similarity_cord19.py              #      
#   (author: Matilde Pato)                                                    #
#                                                                             #   
###############################################################################
#
# This module calculates the similarity between entities and save the results in
# a mysql table. The entities exist on the CORD-19 dataset corpus. Moreover, we 
# add their ancestors to improve resullts
#
# For the CHEBI ontology and if we want to consider the structural similarity,
# we must to include calculate_structural_sim() method in main. 

# Updated: Anyway, if the number of Chebi' entities is large enough, I advise 
# you to perform this operation on the script: calculate_similarity_cord19.py
# Then comment last lines.

# Updated: structural similarity is included in the main

# python3 calculate_similarity_cord19.py   

# Metapub is a Python library that provides python

import os
import sys
import ssmpy
from DiShIn.ssmpy import new_light_similarity
import pandas as pd
from datetime import datetime
# if os.path.isdir( "DiShIn" ):
#    pass
# sys.path.insert( 1, '/KB/src/DiShIn/sspmy/' )
from utils.myconfiguration import MyConfiguration as Config
from multiprocessing import cpu_count, Pool

from utils.utils2ontologies import get_owl_path, get_db_path, loading_items, get_primary_ids
from utils.utils import upload_dataset, save_metadata
from utils.utils2database import check_database, save_to_mysql

pd.set_option('display.max_columns', None)
# pd.set_option("max_rows", None)
pd.options.display.max_rows = 999


# ---------------------------------------------------------------------------------------- #

def update_onto(lexicon):
    '''
    Update ontologies
    '''
    print("Download latest obo files and process lexicons")

    if len(lexicon) == 0:
        lexicon = ["doid", "go", "hpo", "chebi"]
    for l in lexicon:
        # print(l)
        path_owl = get_owl_path(l)
        path_db = get_db_path(l)

        if os.path.isfile(path_db):
            print(f"Database ontology ``{l}.db'' file already exists")
        else:
            ssmpy.create_semantic_base(path_owl, path_db,
                                       "http://purl.obolibrary.org/obo/",
                                       "http://www.w3.org/2000/01/rdf-schema#subClassOf", "")


# ---------------------------------------------------------------------------------------- #

def main():
    import time
    start_time = datetime.now()
    config = Config.get_instance()

    is_chebi, is_doid, is_go, is_hp = False, False, False, False

    path2ds = config.path2ds  # '/ELT/data/results/comm_subset_cord-19_dataset_small.csv'

    active_lexicons = config.item_prefix.replace(' ', '').split(',')
    for item in active_lexicons:
        if item.startswith('chebi'):
            is_chebi = True
        if item.startswith('doid'):
            is_doid = True
        if item.startswith('go'):
            is_go = True
        if item.startswith('hp'):
            is_hp = True

            # ## updating ontologies
    update_onto(active_lexicons)

    # loading ontologies   
    chebi, doid, go, hp = loading_items(is_chebi, is_doid, is_go, is_hp)

    database = config.database

    # connect to mysql table and create if not exists
    check_database(database)

    table_name = config.tablename
    cols_name = ["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc",]# \
                 # "sim_rel", "sim_jac", "sim_islch"]
    df = pd.DataFrame(columns=cols_name)
    count, count_item, count_onto = 0, 0, 0

    for onto in active_lexicons:
        print(onto)
        ssmpy.semantic_base(get_db_path(onto))
        # create_table('_'.join([table_name, onto]))
        # data set contains <user, item, rating>
        df_dataset = upload_dataset(path2ds, onto.upper() + '_')
        # print(df_dataset)
        list_of_entities = df_dataset.item.unique()

        count_onto += 1
        for item in list_of_entities:
            count += 1
            count_item += 1
            print(f'{count_item}:  {item}')
            item_value = item.split('_')[1]
            ancestor = ssmpy.get_ancestors(int(item_value))
            if not ancestor:
                continue

                # create a list of ancestor
            ancestor_ids = [onto.upper() + '_' + str(s) for s in ancestor]
            # get primary id of the CHEBI entity
            if item.startswith('CHEBI') or item.startswith('chebi'):
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

            # # join all entities with his ancestors, and after only select the 25% with higher semantic similarity
            conn = ssmpy.create_connection(get_db_path(onto))
            # df["comp_2"] = ancestor_ids.map(df.set_index('comp_1')).fillna(0)

            ## calculate semantic similarity: resnik, jiang and conrath and lin
            # results = ssmpy.light_similarity(conn, [item], ancestor_ids, 'lin', 20)
            # results = [item for items in results for item in items]
            # sim_df = pd.DataFrame( results, columns=["comp_1", "comp_2", "sim_lin"] )

            ## ------------------------------- ALL ------------------------------ ##
            ## OLDER            
            results = ssmpy.light_similarity(conn, [item], ancestor_ids, 'all', 20)
            results1 = [item for items in results for item in items]
            ## NEWER 
            #results = new_light_similarity(conn, [item], ancestor_ids, 'all', 20)
            #results2 = [item for items in results for item in items]

            sim_df1 = pd.DataFrame(results1, columns=cols_name[:5])
            #sim_df2 = pd.DataFrame(results2, columns=cols_name[:2] + cols_name[5:8])
            #sim_df = sim_df1.merge(sim_df2, on=['comp_1', 'comp_2'])
            sim_df = sim_df1

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
            sim_df = sim_df.loc[~(sim_df[cols_name[2:]] == 0).all(axis=1), :]
            df = pd.concat([df, sim_df], ignore_index=True)

            # check if the table end
            ##  ---------- SAVE ALL IN DB FOR EACH 500 ROWS ---------- ##
            if count > 499:
                # creation of engine to MYSQL database to insert pandas DataFrame in the database
                save_to_mysql(df.drop_duplicates(['comp_1', 'comp_2'], keep='first'), '_'.join([table_name, onto]),
                              onto.upper() + '_')
                # reset all values
                print("***** SAVE IN MYSQL ********")
                df = pd.DataFrame(columns=cols_name)
                sim_df = pd.DataFrame()
                count = 0
                # close connection
                conn.close()
                time.sleep(.5)
            #  ---------- END OF SAVE ALL IN DB FOR EACH 500 ROWS ---------- ##    

        ##  ---------- SAVE ALL REMAINING VALUES IN DB---------- ##     
        if not df.empty:
            # creation of engine to MYSQL database to insert pandas DataFrame in the database
            save_to_mysql(df.drop_duplicates(['comp_1', 'comp_2'], keep='first'), '_'.join([table_name, onto]),
                          onto.upper() + '_')
            # reset all values
            df = pd.DataFrame(columns=cols_name)
            sim_df = pd.DataFrame()
            count = 0
            # close connection
            conn.close()
            ##  ---------- END OF SAVE ALL REMAINING VALUES IN DB---------- ##

    # if is_chebi:    
    #    calculate_structural_sim('_'.join([table_name,'chebi']))  

    # ---------------------------------------------------------------------------------------- #
    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\t No. entities: {count_item}\n\
                Results: {config.path2kb, path2ds}\n\
                '
    save_metadata(config.path2info, metadata)
    print("FINISHED!")


# ---------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()
