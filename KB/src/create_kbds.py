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
#   version 1.2: 21 Feb 2023 change pd.append() by pd.concat()                #      
#   (author: Matilde Pato, matilde.pato@gmail.com)                            #  
#                                                                             #   
###############################################################################
#
# This module create CORD-19 corpus dataset with is ancestors as:
# <user, item, rating, item_name, year>.
# The items should be defined by user

# python3 create_kbds.py

# Metapub is a Python library that provides python

import os
import ssmpy
import pandas as pd
import numpy as np
from datetime import datetime

from utils.myconfiguration import MyConfiguration as Config
from utils.utils2ontologies import get_owl_path, get_db_path, loading_items, get_entities_labels
from utils.utils import upload_dataset, save_to_csv, save_metadata
from utils.utils2database import check_database, get_similar

pd.set_option('display.max_columns', None)


def update_onto(lexicon_list):
    """
    Update ontologies
    """
    print("Download latest obo files and process lexicons")

    if len(lexicon_list) == 0:
        lexicon_list = ["doid", "go", "hpo", "chebi"]
    for lexicon in lexicon_list:
        path_owl = get_owl_path(lexicon)
        path_db = get_db_path(lexicon)

        if os.path.isfile(path_db):
            print(f"Database ontology ``{lexicon}.db'' file already exists")
        else:
            ssmpy.create_semantic_base(
                path_owl,
                path_db,
                "http://purl.obolibrary.org/obo/",
                "http://www.w3.org/2000/01/rdf-schema#subClassOf",
                ""
            )


def id2index(df):
    """
    maps the values to the lowest consecutive values
    :param df: pandas Dataframe with columns user, item, rating
    :return: pandas Dataframe with the columns index_item and index_user
    """

    index_user = np.arange(0, len(df.user.unique()))

    df_user_index = pd.DataFrame(df.user.unique(), columns=["user"])
    df_user_index["new_index"] = index_user

    df["index_user"] = df["user"].map(df_user_index.set_index('user')["new_index"]).fillna(0)
    return df


def main():
    start_time = datetime.now()
    config = Config.get_instance()

    # # define most common in percentage, by default is 'first quartile'
    quartile_percentage = config.n
    normalized = config.normalized

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

            # # ## updating ontologies
    update_onto(active_lexicons)

    # loading ontologies
    chebi, doid, go, hp = loading_items(is_chebi, is_doid, is_go, is_hp)

    # connect to mysql table
    database = config.database
    check_database(database)

    count = 0
    for onto in active_lexicons:
        print(f'onto: {onto}')

        cols_name = [
            "comp_1",
            "comp_2",
            "sim_resnik",
            "sim_lin",
            "sim_jc",
        ]
        if onto.startswith('chebi'):
            cols_name.extend(["sim_tanimoto", "sim_morgan"])

        def similarity_table(i):
            return 'similarity_structural' if (i == "sim_tanimoto" or i == "sim_morgan") else config.tablename

        for s in cols_name[2:]:
            print(f'Processing similarity dataset for {s}')
            count += 1
            # data set contains <user, item, rating>
            df_ds = upload_dataset(path2ds, onto.upper() + '_')

            # Get n% from all normalized similarity with l2 metric
            if normalized:
                print('Using normalized similarity')
                sim_table = '_'.join(['norm', similarity_table(s), onto, s])
                df_similar = get_similar(sim_table, quartile_percentage, metric='l2')
            else:
                df_similar = get_similar('_'.join([similarity_table(s), onto]), quartile_percentage, metric=s)

            df_similar.comp_1 = onto.upper() + '_' + df_similar.comp_1.map(str)
            df_similar.comp_2 = onto.upper() + '_' + df_similar.comp_2.map(str)

            idx = []

            # find index where item1 exist in dataframe
            for item1 in df_ds[['item']].drop_duplicates().values.tolist():
                idx = df_ds.index[df_ds['item'] == ''.join(item1)].tolist()
                # get item2 list 
                item2 = df_similar[df_similar['comp_1'] == ''.join(item1)]['comp_2']
                # if the entity has no ancestor, continue
                if item2.empty:
                    continue
            print('Loop completed')
            # pair = pd.DataFrame(
            #     [
            #         {
            #             'user': df_ds.at[i, 'user'],
            #             'username': df_ds.at[i, 'username'],
            #             'item': c,
            #             'rating': df_ds.at[i, 'rating'],
            #             'year': df_ds.at[i, 'year']
            #         }
            #         for i in idx for c in item
            #     ]
            # )
            # append values from original dataframe and sort by user
            # df_ds = pd.concat([df_ds, pair], ignore_index=True)
            df_ds = df_ds.sort_values(by=['user']).reset_index(drop=True)

            sum_df = df_ds.groupby(
                ['user', 'username', 'item', 'year']
            ).size().reset_index().rename(columns={0: 'rating'})
            df_id = id2index(sum_df)

            # Get entities labels
            list_of_entities = df_id.item.unique()
            # print(list_of_entities) 

            entities_label = get_entities_labels(list_of_entities, chebi, doid, go, hp)
            # entities_label = get_entities_labels(list_of_entities, None, None, None, None)
            df_entities = pd.DataFrame(list_of_entities, columns=["item_id"])
            df_entities["entity_name"] = np.array(entities_label)

            print('mapping labels')
            df_id["item_name"] = df_id["item"].map(df_entities.set_index('item_id')["entity_name"]).fillna(0)

            print('saving data')
            path = '_'.join([config.path2kb.rsplit('.', 1)[0], onto, s, '.csv'])

            if 'year' in df_id.columns:
                save_to_csv(
                    df=df_id[['user', 'username', 'item', 'item_name', 'rating', 'year']],
                    header=True,
                    path=path
                )
            else:
                save_to_csv(
                    df=df_id[['user', 'username', 'item', 'item_name', 'rating']],
                    header=True,
                    path=path
                )

    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\n\
                Results: {config.path2kb, path2ds}\n\
                '
    save_metadata(config.path2info, metadata)
    print("FINISHED!")


if __name__ == '__main__':
    main()
