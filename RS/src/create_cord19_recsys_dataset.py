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
# @date: 31 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#  (Adapted from Pedro Ruas)                                                  #  
# @last update:                                                               #  
#   version 1.1:                                                              #      
#   (author: 22 April 2021  )                                                 # 
#                                                                             #   
#                                                                             #  
###############################################################################
#
# This module create CORD-19 corpus dataset as <user, item, rating, item_name, year>
# and <user_id, author_name>. The items should be defined by user

# python3 create_cord19_recsys_dataset.py   

# Metapub is a Python library that provides python

import pandas as pd
import sys
import json
import numpy as np
import time
from datetime import date, datetime
import configargparse

from myconfiguration import MyConfiguration as cfg
from Utils.utils import *
from Utils.utils2json import *
from Utils.utils2metadata import *
from Utils.utils2pubmed import *
from Utils.utils2ontologies import *
from functions import *

pd.set_option('display.max_columns', None)
pd.set_option("max_rows", None)

# ---------------------------------------------------------------------------------------- #

def get_authors_names(data, csv_metadata):

    list_of_authors = get_authors_json(data)
    #print('json: ', list_of_authors)
    if len(list_of_authors)==0:

        list_of_authors = get_authors_csvmetadata(data=csv_metadata, ident=get_article_id(data))
        print('csv: ', list_of_authors)
        if len(list_of_authors)==0 & len(get_pmcid_csvmetadata(csv_metadata, data))!=0:
            list_of_authors = get_authors_by_metapub(pmcid=get_pmcid_csvmetadata(csv_metadata, data))
            #print('meta: ', list_of_authors)
            if len(list_of_authors)==0:
                pmid = get_pmid(pmcid=get_pmcid_csvmetadata(csv_metadata, data))
                list_of_authors = get_authors_by_bio(pmid)
                #print('bio: ', list_of_authors)
            else:
                return []     
    # print(list_of_authors)   
    return list_of_authors

# ---------------------------------------------------------------------------------------- #

def get_date(data, csv_metadata):

    if data.startswith('PMC'):
        id_file = 'pmcid'
    else:
        id_file = 'sha'

    try:
        publish_date = csv_metadata[csv_metadata[id_file] == data].publish_time.map(lambda v: v.split('-')[0]).tolist()[0]
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
                if len(get_pmcid_csvmetadata(csv_metadata, data))!=0:
                    pmid = get_pmid(pmcid=get_pmcid_csvmetadata(csv_metadata, data))
                    publish_date = get_year_by_bio(pmid)    
                    print('bio: ', publish_date)        
                else:    
                    publish_date = None

    return publish_date

# ---------------------------------------------------------------------------------------- #

def main():

    start_time = datetime.now()
    
    arg = cfg.getInstance()
    is_chebi, is_cido, is_do, is_go, is_hp, is_taxon = False, False, False, False, False, False

    # if entities is defined by user then saved it in a list
    active_lexicons = []
    if arg.item_prefix1.startswith('chebi'):
        is_chebi = True
        active_lexicons.append('chebi')   
    if arg.item_prefix2.startswith('do'):
        is_do = True
        active_lexicons.append('do')      
    if arg.item_prefix3.startswith('go'):
        is_go = True
        active_lexicons.append('go')  
    if arg.item_prefix4.startswith('hp'):
        is_hp = True
        active_lexicons.append('hp')      
    #is_cido = is_taxon 

    entities_list_of_json_files = list_files_in_directory(arg.entities_json_folder)
    
    # get all articles id that cannot be considered in use case 
    articles_blacklist = get_blacklist(file=arg.path_to_blacklist)
    #print(articles_blacklist)
    metadata = pd.read_csv(arg.path_to_metadata)

    user_item_rating_all = []

    count = -1
    for file in entities_list_of_json_files:
        count+=1
        # ## Exception
        if file in articles_blacklist:
            continue
        # if file.startswith('PMC'):
        #     continue    
        print(count, "-", len(entities_list_of_json_files), ': ', file)            
           
        # check valid json file, i.e. contains values
        try:
            j_file_entities = pd.read_json(arg.entities_json_folder + file, orient = 'index')
        except Exception as e:
            print(f'Json file does not contain values. Error message {e}')
            set_blacklist(arg.path_to_blacklist, file.replace('_entities.json',''))
            continue
        
        # get the list of entities and respectively number of times
        dict_entities = j_file_entities.loc['entities'][0]
        df_entities = pd.DataFrame(dict_entities.items(), columns=['entities', 'count'])
        df_entities['entities_id'] = df_entities.entities.str.split(pat="/").str[-1]

        if df_entities.empty:
            print(f'Json file does not contain values.')
            set_blacklist(arg.path_to_blacklist, file.replace('_entities.json',''))
            continue    
        
        article_id = j_file_entities.loc['id'].values[0]

        # check valid json file, i.e. contains values
        try:
            j_file_original = open_json_file(arg.original_json_folder, article_id)
            #print(j_file_original)
        except Exception as e:
            print(f'Original json file does not exist. Error message {e}')
            set_blacklist(arg.path_to_blacklist, file.replace('_entities.json',''))
            continue    

        # check if json file contains authors, otherwise try to find them in metadata.csv
        # if value remains null them put this article in the blacklist file
        list_of_authors = get_authors_names(data=j_file_original, csv_metadata=metadata)
        
        #print(list_of_authors)
        if len(list_of_authors)==0:
            print(f'Authors list does not exist.')
            set_blacklist(arg.path_to_blacklist, file.replace('_entities.json',''))
            continue  

        # Get date (year)
        try:
            publish_date = get_date(data=article_id, csv_metadata=metadata)
            # print(publish_date)
        except Exception as e:
            print(f'Date does not exist. Error message {e}')
            set_blacklist(arg.path_to_blacklist, file.replace('_entities.json',''))
            continue   

        user_item_rating = get_user_item_rating(list_of_authors, df_entities)
        # print(user_item_rating)
        
        ## add publish_date in array in index column = 3
        user_item_rating = np.insert(user_item_rating, 3, publish_date, axis=1)
        # print(user_item_rating)
        user_item_rating_all.append(user_item_rating)

        # if count > 0:
        #     break

    flat_list = []
    for sublist in user_item_rating_all:
        for item in sublist:
            flat_list.append(item)

    array = np.array(flat_list)

    final_data = pd.DataFrame(array,  columns=['user', 'item', 'rating', 'year'])

    sum_df = final_data.groupby(['user', 'item', 'year']).size().reset_index().rename(columns={0: 'rating'})
    
    df_with_user_id = id_to_index(sum_df)

    # swap columns: user and index_user, and after rename to author_name
    #df_with_user_id['index_user'], df_with_user_id['user'] = df_with_user_id['user'], df_with_user_id['index_user']
    df_with_user_id.rename(columns={'user': 'author_name', 'index_user': 'user'}, inplace = True)

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
    save_final_data(data=df_with_user_id[['user', 'item', 'rating', 'item_name', 'year']], \
        path=arg.path_to_cord_ds)
    save_final_data(data=df_with_user_id[['user', 'author_name']], \
        path=arg.path_to_cord_userid)

    save_final_data(data=df_with_user_id[['user', 'author_name', 'item', 'rating', 'item_name', 'year']], \
        path=arg.path_to_cord_all)
    # ---------------------------------------------------------------------------------------- #
    
    ## save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\n\
                No. articles: {count}\n\
                Results: {arg.path_to_cord_userid, arg.path_to_cord_ds}\n\
                '
    save_metadata(arg.path_to_info, metadata) 
 
# ---------------------------------------------------------------------------------------- #
 
# ---------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()