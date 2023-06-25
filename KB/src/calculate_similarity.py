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
#   new script to calculate them: calculate_similarity.py              #
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
# you to perform this operation on the script: calculate_similarity.py
# Then comment last lines.

# Updated: structural similarity is included in the main

# python3 calculate_similarity.py

# Metapub is a Python library that provides python

import os
import time
import ssmpy
import pandas as pd
from datetime import datetime
from utils.myconfiguration import MyConfiguration as Config

from utils.utils2ontologies import get_owl_path, get_db_path, loading_items, get_primary_ids
from utils.utils import upload_dataset, save_metadata
from utils.utils2database import check_database, save_to_mysql, check_table

pd.set_option('display.max_columns', None)
pd.options.display.max_rows = 999


def update_onto(lexicons):
    """
    Update ontologies
    """
    print("Download latest obo files and process lexicons")

    if len(lexicons) == 0:
        lexicons = ["doid", "chebi"]
    for lexicon in lexicons:
        path_owl = get_owl_path(lexicon)
        path_db = get_db_path(lexicon)

        if os.path.isfile(path_db):
            print(f"Database ontology ``{lexicon}.db'' file already exists")
        else:
            ssmpy.create_semantic_base(path_owl, path_db,
                                       "http://purl.obolibrary.org/obo/",
                                       "http://www.w3.org/2000/01/rdf-schema#subClassOf", "")


def process_item(item, onto, chebi, cols_name, item_idx):
    print(f'{item_idx}:  {item}')

    config: Config = Config.get_instance()
    df = pd.DataFrame(columns=cols_name)
    table_name = config.tablename
    item_value = item.split('_')[1]
    print('Getting ancestors')
    ancestor = ssmpy.get_ancestors(int(item_value))
    if not ancestor:
        return

    # create a list of ancestor
    ancestor_ids = [onto.upper() + '_' + str(s) for s in ancestor]
    # get primary id of the CHEBI entity
    if item.startswith('CHEBI') or item.startswith('chebi'):
        ancestor_ids = get_primary_ids(ancestor_ids, chebi)

    # join all entities with his ancestors, and after only select the 25% with higher semantic similarity
    conn = ssmpy.create_connection(get_db_path(onto))

    print('Calculating similarities')
    results = ssmpy.light_similarity(conn, [item], ancestor_ids, 'all', 20)
    results1 = [item for items in results for item in items]

    sim_df1 = pd.DataFrame(results1, columns=cols_name[:5])
    sim_df = sim_df1

    # remove rows where entities are equal (avoid sim = 1)
    sim_df = sim_df[sim_df['comp_1'] != sim_df['comp_2']]
    sim_df = sim_df.loc[~(sim_df[cols_name[2:]] == 0).all(axis=1), :]
    df = pd.concat([df, sim_df], ignore_index=True)

    print('Saving ancestors to MySQL')
    # creation of engine to MYSQL database to insert pandas DataFrame in the database
    save_to_mysql(
        df.drop_duplicates(['comp_1', 'comp_2'], keep='first'),
        '_'.join([table_name, onto]),
        onto.upper() + '_'
    )
    print("***** SAVED IN MYSQL ********")
    # close connection
    conn.close()
    time.sleep(.5)


def main():
    start_time = datetime.now()
    config: Config = Config.get_instance()

    is_chebi, is_doid = False, False

    path2ds = config.path2ds  # '/ELT/data/results/comm_subset_cord-19_dataset_small.csv'

    active_lexicons = config.item_prefix.replace(' ', '').split(',')
    for item in active_lexicons:
        if item.startswith('chebi'):
            is_chebi = True
        if item.startswith('doid'):
            is_doid = True

            # ## updating ontologies
    update_onto(active_lexicons)

    # loading ontologies
    chebi, _, _, _ = loading_items(is_chebi=is_chebi, is_doid=is_doid)

    database_name = config.database
    table_name = config.tablename

    # connect to mysql table and create if not exists
    check_database(database_name)

    cols_name = ["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc"]
    count, count_item, count_onto = 0, 0, 0

    for onto in active_lexicons:
        print(onto)
        check_table(database_name, '_'.join([table_name, onto]))
        ssmpy.semantic_base(get_db_path(onto))
        # data set contains <user, item, rating>
        df_dataset = upload_dataset(path2ds, onto.upper() + '_')
        list_of_entities = df_dataset.item.unique()

        count_onto += 1
        for item in list_of_entities:
            process_item(item, onto, chebi, cols_name, count_item)
            count_item += 1

    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\t No. entities: {count_item}\n\
                Results: {config.path2kb, path2ds}\n\
                '
    save_metadata(config.path2info, metadata)
    print("FINISHED!")


if __name__ == '__main__':
    main()
