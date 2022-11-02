###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 31 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#  (Adapted from Pedro Ruas)                                                  #  
# @last update:                                                               #  
#   version 1.1: 25 May 2022 - add sleep counter, create an auxiliar functions#
#   to create the <user, item, rating, year> dataset                          #      
#   (author: matilde.pato@gmail.com  )                                        # 
#                                                                             #   
#                                                                             #  
###############################################################################
#
# This module create CORD-19 corpus dataset as <user, item, rating, item_name, year>
# and <user_id, author_name>. The items should be defined by user

# python3 create_cord19_recsys_dataset.py   

# Metapub is a Python library that provides python

import pandas as pd
import numpy as np
from datetime import datetime

from myconfiguration import MyConfiguration as cfg
from Utils.utils import get_blacklist, set_blacklist, save_to_csv, save_metadata
from Utils.utils2json import *
from Utils.utils2metadata import *
from Utils.utils2pubmed import *
from Utils.utils2ontologies import *
from functions import *

pd.set_option('display.max_columns', None)
pd.set_option("max_rows", None)

# ---------------------------------------------------------------------------------------- #

def get_authors_names(doc, csv_metadata):


    list_of_authors = get_authors_json(doc=doc)
    #print('json: ', list_of_authors)
    if len(list_of_authors)==0:

        list_of_authors = get_authors_csvmetadata(csv=csv_metadata, ident=get_article_id(doc))

        if len(list_of_authors)==0 & len(get_pmcid_csvmetadata(cvs=csv_metadata, ident=get_article_id(doc)))!=0:
            list_of_authors = get_authors_by_metapub(pmcid=get_pmcid_csvmetadata(csv_metadata, ident=get_article_id(doc)))
            #print('meta: ', list_of_authors)
            if len(list_of_authors)==0:
                pmid = get_pmid(pmcid=get_pmcid_csvmetadata(csv=csv_metadata, ident=get_article_id(doc)))
                list_of_authors = get_authors_by_bio(pmid)
                #print('bio: ', list_of_authors)
            else:
                return []     
    # print(list_of_authors)   
    return list_of_authors

# ---------------------------------------------------------------------------------------- #

def get_date(data, csv):

    if data.startswith('PMC'):
        id_file = 'pmcid'
    else:
        id_file = 'sha'

    try:
        publish_date = csv[csv[id_file] == data].publish_time.map(lambda v: v.split('-')[0]).tolist()[0]
        ## before 2020-05-19:
        # # format is YYYY month DD
        if len(publish_date) > 4:           
            publish_date = publish_date.map(lambda v: v.split(' ')[2])
    except Exception as e:
        print(f'Date does not exist in csv metadata. Error message {e}')  
        publish_date = None
    
    if data.startswith('PMC'):
        if publish_date is None:
            publish_date = get_year_by_metapub(pmcid=data)
            if publish_date is None: 
                if len(get_pmcid_csvmetadata(csv, ident=data))!=0:
                    pmid = get_pmid(pmcid=get_pmcid_csvmetadata(csv, ident=data))
                    publish_date = get_year_by_bio(pmid)    
                    print('bio: ', publish_date)        
                else:    
                    publish_date = None

    return publish_date

# ---------------------------------------------------------------------------------------- #

def create_dataset(path_original, path_entities, path_metadata, path_blacklist):
    """
    create the dataset with parameters <user, item, rating, year>
    :param path_original: path of original json files
    :param path_entities: path of entities json files
    :param path_metadata: path of the metadata csv files
    :param path_blacklist: path with the blacklist (list of non-validate files)
    :return count: number of files processed (only for metadata)
    :return user_item_rating_all: list with <user, item, rating, year> values
    """

    import time
    user_item_rating_all = []
    entities_list_of_json_files = os.listdir(path_entities)
    
    # get all articles id that cannot be considered in use case 
    articles_blacklist = get_blacklist(file=path_blacklist)
    #print(articles_blacklist)
    metadata = pd.read_csv(path_metadata)

    count = -1
    count_sleep = -1
    for file in entities_list_of_json_files:
        count+=1
        count_sleep+=1
        # ## Exception
        if file in articles_blacklist:
            continue
        # if file.startswith('PMC'):
        #     continue    
        print(count, "-", len(entities_list_of_json_files), ': ', file)            
           
        # check valid json file, i.e. contains values
        try:
            j_file_entities = pd.read_json(path_entities + file, orient = 'index')
        except Exception as e:
            print(f'Json file does not contain values. Error message {e}')
            set_blacklist(path_blacklist, file.replace('_entities.json',''))
            continue
        
        # get the list of entities and respectively number of times
        dict_entities = j_file_entities.loc['entities'][0]
        df_entities = pd.DataFrame(dict_entities.items(), columns=['entities', 'count'])
        df_entities['entities_id'] = df_entities.entities.str.split(pat="/").str[-1]
       
        if df_entities.empty:
            print(f'Json file does not contain values.')
            set_blacklist(path_blacklist, file.replace('_entities.json',''))
            continue    
        
        article_id = j_file_entities.loc['id'].values[0]

        # check valid json file, i.e. contains values
        try:
            j_file_original = open_json_file(path_original, article_id)
            #print(j_file_original)
        except Exception as e:
            print(f'Original json file does not exist. Error message {e}')
            set_blacklist(path_blacklist, file.replace('_entities.json',''))
            continue    

        # check if json file contains authors, otherwise try to find them in metadata.csv
        # if value remains null them put this article in the blacklist file
        list_of_authors = get_authors_names(doc=j_file_original, csv_metadata=metadata)
        
        #print(list_of_authors)
        if len(list_of_authors)==0:
            print(f'Authors list does not exist.')
            set_blacklist(path_blacklist, file.replace('_entities.json',''))
            continue  

        # Get date (year)
        try:
            publish_date = get_date(data=article_id, csv=metadata)
            # print(publish_date)
        except Exception as e:
            print(f'Date does not exist. Error message {e}')
            set_blacklist(path_blacklist, file.replace('_entities.json',''))
            continue   

        user_item_rating = get_user_item_rating(list_of_authors, df_entities)
        # print(user_item_rating)
        
        ## add publish_date in array in index column = 3
        user_item_rating = np.insert(user_item_rating, 3, publish_date, axis=1)
        # print(user_item_rating)
        user_item_rating_all.append(user_item_rating)

        if count_sleep > 999:
            time.sleep(0.5)
            count_sleep=-1   
             
    return count, user_item_rating_all       

# ---------------------------------------------------------------------------------------- #

def main():

    start_time = datetime.now()

    arg = cfg.getInstance()
    is_chebi, is_cido, is_do, is_go, is_hp, is_taxon = False, False, False, False, False, False

    # if entities is defined by user then saved it in a list
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

    # create the dataset with <user, item, rating, year> values
    nfiles, user_item_rating_all = create_dataset(path_original = arg.original_json_folder , \
        path_entities = arg.entities_json_folder, path_metadata = arg.path_to_metadata, \
            path_blacklist = arg.path_to_blacklist)

    flat_list = []
    for sublist in user_item_rating_all:
        for item in sublist:
            flat_list.append(item)

    array = np.array(flat_list)

    final_data = pd.DataFrame(array,  columns=['user', 'item', 'rating', 'year'])

    sum_df = final_data.groupby(['user', 'item', 'year']).size().reset_index().rename(columns={0: 'rating'})
    
    df_with_user_id = id_to_index(sum_df)

    # swap columns: user and index_user, and after rename to user_name
    #df_with_user_id['index_user'], df_with_user_id['user'] = df_with_user_id['user'], df_with_user_id['index_user']
    df_with_user_id.rename(columns={'user': 'user_name', 'index_user': 'user'}, inplace = True)

    # get entities labels
    list_of_entities = df_with_user_id.item.unique()
    #print(list_of_entities) 

    # loading ontologies   
    chebi, do, go, hp = loading_items(is_chebi, is_do, is_go, is_hp)

    # entities_label = get_entities_labels(list_of_entities, chebi, hp, go, do)
    entities_label = get_entities_labels(list_of_entities, chebi, do, go, hp)
    #print(entities_label)

    df_entities = pd.DataFrame(list_of_entities, columns=["item_id"])
    df_entities["entity_name"] = np.array(entities_label)

    print('mapping labels')
    df_with_user_id["item_name"] = df_with_user_id["item"].map(df_entities.set_index('item_id')["entity_name"]).fillna(0)
    
    # swap columns: rating 2 item_name
    #df_with_user_id['rating'], df_with_user_id['item_name'] = df_with_user_id['item_name'], df_with_user_id['rating']
    #df_with_user_id.rename(columns={'rating': 'item_name', 'item_name': 'rating'}, inplace = True)

    print('saving data')
    save_to_csv(df=df_with_user_id[['user', 'user_name', 'item', 'rating', 'item_name', 'year']], \
        path=arg.path_to_cord_all)
    # ---------------------------------------------------------------------------------------- #
    
    ## save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\n\
                No. articles: {nfiles}\n\
                Results: {arg.path_to_cord_userid, arg.path_to_cord_ds}\n\
                '
    save_metadata(arg.path_to_info, metadata) 
    print("FINISHED!")

# ---------------------------------------------------------------------------------------- #
 
# ---------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()