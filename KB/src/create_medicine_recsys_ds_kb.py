###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 16 Nov 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
# @last update:                                                               #  
#   version 1.1: 27 July 2022                                                 #      
#   (author: matilde.pato@gmail.com )                                         # 
#                                                                             #   
###############################################################################
#
# This module create CORD-19 corpus dataset with is ancestors as:
# <user, item, rating, item_name, year>.
# The items should be defined by user

# python3 create_cord19_recsys_ds_kb.py   

# Metapub is a Python library that provides python

import os
import sys
import ssmpy
import pandas as pd
import numpy as np
import sqlite3
from tracemalloc import stop
from datetime import datetime
from scipy import stats
from myconfiguration import MyConfiguration as cfg
from Utils.utils2ontologies import get_owl_path, get_db_path, loading_items, get_entities_labels
from Utils.utils import upload_dataset, save_to_csv, save_metadata
from Utils.utils2database import check_database, get_similar, check_structural_chebi

if os.path.isdir("DiShIn"):
    pass
sys.path.insert(1, '/KB/src/DiShIn/sspmy/')

pd.set_option('display.max_columns', None)
pd.set_option("max_rows", None)


# ---------------------------------------------------------------------------------------- #

def update_onto(lexicon):
    """
    Update ontologies
    """
    print("Download latest obo files and process lexicons")

    if len(lexicon) == 0:
        lexicon = ["doid", "go", "hpo", "chebi"]
    for l in lexicon:
        print(l)
        path_owl = get_owl_path(l)
        path_db = get_db_path(l)

        if os.path.isfile(path_db):
            print(f"Database ontology ``{l}.db'' file already exists")
        else:
            ssmpy.create_semantic_base(path_owl, path_db,
                                       "http://purl.obolibrary.org/obo/",
                                       "http://www.w3.org/2000/01/rdf-schema#subClassOf", "")


# ---------------------------------------------------------------------------------------- #

def id_to_index(df):
    """
    maps the values to the lowest consecutive values
    :param df: pandas Dataframe with columns user, item, rating
    :return: pandas Dataframe with the columns index_item and index_user
    """

    index_user = np.arange(0, len(df.user.unique()))

    df_user_index = pd.DataFrame(df.user.unique(), columns=["user"])
    df_user_index["new_index"] = index_user

    df["index_user"] = df["user"].map(df_user_index.set_index('user')["new_index"]).fillna(0)
    # print(df)
    return df


# ---------------------------------------------------------------------------------------- #


def main():
    import time
    start_time = datetime.now()
    arg = cfg.getInstance()

    # # define most common in percentage, by default is 'first quartile'
    quartile = arg.n

    is_chebi, is_do, is_go, is_hp = False, False, False, False

    path_to_ds = arg.path_to_ds  # '/ELT/data/results/comm_subset_cord-19_dataset_small.csv'

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

            # # ## updating ontologies
    update_onto(active_lexicons)

    # # # loading ontologies   
    chebi, do, go, hp = loading_items(is_chebi, is_do, is_go, is_hp)

    # # ---------------------------------------------------------------------------------------- #
    # # connect to mysql table
    check_database()

    count = 0
    for onto in active_lexicons:
        print(f'onto: {onto}')

        cols_name = ["comp_1", "comp_2", "sim_tanimoto", "sim_resnik", "sim_lin", "sim_jc", "sim_rel", "sim_jac",
                     "sim_islch"]

        for s in cols_name[2:]:
            print(f'sim: {s}')

            if s.startswith('sim_tanimoto'):
                if onto.startswith('chebi') and check_structural_chebi('similarity_structural_chebi'):
                    table_name = 'similarity_structural'
                elif onto.startswith('doid'):
                    continue
            else:
                table_name = arg.tablename

            # ssmpy.semantic_base(get_db_path(onto))
            # create_table('_'.join([table_name,onto]))
            # data set contains <user, item, rating>
            df_ds = upload_dataset(path_to_ds, onto.upper() + '_')

            #  ---------- GET ENTITIES LABELS OF THE 1st QUARTILE ---------- ##

            df_similar = get_similar('_'.join([table_name, onto]), quartile, sim=s)
            df_similar.comp_1 = onto.upper() + '_' + df_similar.comp_1.map(str)
            df_similar.comp_2 = onto.upper() + '_' + df_similar.comp_2.map(str)
            # print(df_similar[['comp_1', 'comp_2']].head(10))

            # # --- example
            # df_ds = pd.DataFrame(np.array([[0,'CHEBI_15361', 1, 2021], [0,'CHEBI_15378', 1, 2021], [0,'CHEBI_15362', 1, 2021], \
            #     [17,'CHEBI_15361', 1, 2021], [52,'CHEBI_15361', 1, 2021], [67,'CHEBI_15361', 1, 2021]]), columns=['user', 'item', 'rating','year'])
            # #
            # # item1 = 'CHEBI_15361'
            # # item2 = ['CHEBI_103229', 'CHEBI_150', 'CHEBI_17818', 'CHEBI_24156', \
            # #     'CHEBI_34386', 'CHEBI_50934', 'CHEBI_51286', 'CHEBI_66106', 'CHEBI_8186', 'CHEBI_88',\
            # #     'CHEBI_96062'] 
            # # --- end of example

            # find index where item1 exist in dataframe
            for item1 in df_ds[['item']].drop_duplicates().values.tolist():
                idx = df_ds.index[df_ds['item'] == ''.join(item1)].tolist()
                # get item2 list 
                item2 = df_similar[df_similar['comp_1'] == ''.join(item1)]['comp_2']
                # if the entity has no ancestor, continue
                if item2.empty:
                    continue

            pair = [{'user': df_ds.at[i, 'user'], 'user_name': df_ds.at[i, 'user_name'], 'item': c, \
                     'rating': df_ds.at[i, 'rating'], 'year': df_ds.at[i, 'year']} for i in idx for c in item]
            # append values from orginal dataframe and sort by user
            df_ds = df_ds.append(pair, ignore_index=True).sort_values(by=['user']).reset_index(drop=True)

            sum_df = df_ds.groupby(['user', 'user_name', 'item', 'year']).size().reset_index().rename(
                columns={0: 'rating'})
            df_id = id_to_index(sum_df)
            # print(f"df_id: {df_id.head(10)}")

            # count += 1
            # if count>0:
            #     break

            # ## ---------- get entities labels ----------
            list_of_entities = df_id.item.unique()
            # print(list_of_entities) 

            entities_label = get_entities_labels(list_of_entities, chebi, do, go, hp)
            df_entities = pd.DataFrame(list_of_entities, columns=["item_id"])
            df_entities["entity_name"] = np.array(entities_label)

            print('mapping labels')
            df_id["item_name"] = df_id["item"].map(df_entities.set_index('item_id')["entity_name"]).fillna(0)

            print('saving data')
            path = '_'.join([arg.path_to_kb_all.split('.')[0], s, '.csv'])
            path = path.split('.')[0] + onto + '.csv'

            if 'year' in df_id.columns:
                save_to_csv(df=df_id[['user', 'user_name', 'item', 'item_name', 'rating', 'year']], \
                            path=path)
            else:
                save_to_csv(df=df_id[['user', 'user_name', 'item', 'rating', 'item_name']], \
                            path=path)

                # count += 1
            # if count>2:
            #     break        

    # ---------------------------------------------------------------------------------------- #

    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\n\
                Results: {arg.path_to_kb_all, path_to_ds}\n\
                '
    save_metadata(arg.path_to_info, metadata)
    print("FINISHED!")


# ---------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()
