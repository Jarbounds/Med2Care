
###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 03 May 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 28 May 2021 - change textblob to googletrans                 #      
#   (author: matilde.pato@gmail.com  )                                        # 
#   version 1.2: 01 Oct 2021 - Remove googletrans and use langdetect          #  
#   check valid author names with spacy                                       #      
#   (author: matilde.pato@gmail.com  )                                        #    
#   version 1.3: 27 Mar 2022 - Check date if exist, put blacklist in dict and #
#   save at the end                                                           #    
#   (author: matilde.pato@gmail.com  )                                        #  
#   version 1.4: 26 May 2022 - Add config.ini file                            #    
#   (author: matilde.pato@gmail.com  )                                        #    
#                                                                             #  
###############################################################################
#
# Find non valid articles after remove duplicate files, such as without authors
# (or, not valid), add abstract where non-found, and language is different from 
# predefined and write the paper_id to a txt files as a blacklist

# python3 cleaning_data.py 

import sys
import os
from pathlib import Path
import shutil
import pandas as pd
import unidecode
import re 
from langdetect import detect
import configparser


from Utils.utils2pubmed import get_authors_by_metapub, get_authors_by_bio, get_pmid, get_year_by_metapub, get_year_by_bio
from Utils.utils import  set_blacklist
from Utils.utils2metadata import get_authors_csvmetadata, get_pmcid_csvmetadata
from Utils.utils2json import open_json_file, get_authors_json, get_title_json, get_article_id

# ---------------------------------------------------------------------------------------- #

def get_authors_names(data, csv):
    '''
    Return list of authors if any
    
    :param  data: name of json file
    :param  csv: name of metadata
    :return lst_of_authors      
    '''

    list_of_authors = get_authors_json(data)
    #print('json: ', list_of_authors)
    if len(list_of_authors)==0:

        list_of_authors = get_authors_csvmetadata(data=csv, ident=get_article_id(data))

        if len(list_of_authors)==0 & len(get_pmcid_csvmetadata(csv, data))!=0:
            list_of_authors = get_authors_by_metapub(pmcid=get_pmcid_csvmetadata(csv, data))
            #print('meta: ', list_of_authors)
            if len(list_of_authors)==0:
                pmid = get_pmid(pmcid=get_pmcid_csvmetadata(csv, data))
                list_of_authors = get_authors_by_bio(pmid)
                #print('bio: ', list_of_authors)
            else:
                return []     
    # print(list_of_authors)   
    return list_of_authors

# ---------------------------------------------------------------------------------------- #

def get_date(data, csv):
    '''
    Return year of the article if exist
    
    :param  data: name of json file
    :param  csv: name of metadata
    :return publish_date      
    '''

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
                if len(get_pmcid_csvmetadata(csv, data))!=0:
                    pmid = get_pmid(pmcid=get_pmcid_csvmetadata(csv, data))
                    publish_date = get_year_by_bio(pmid)    
                    print('bio: ', publish_date)        
                else:    
                    publish_date = None

    return publish_date

# ---------------------------------------------------------------------------------------- #

def check_language(data, language):

    '''
    Language avaiable:
    af, ar, bg, bn, ca, cs, cy, da, de, el, en, es, et, fa, fi, fr, gu, he,
    hi, hr, hu, id, it, ja, kn, ko, lt, lv, mk, ml, mr, ne, nl, no, pa, pl,
    pt, ro, ru, sk, sl, so, sq, sv, sw, ta, te, th, tl, tr, uk, ur, vi, zh-cn, zh-tw    
    '''
    
    language=language.split(', ')
    for l in language: 
        try:
            if detect(data)==l:
                return True
        except:
            False        
    return False

# ---------------------------------------------------------------------------------------- #
       

def main(): #lang, list_of_json_files):

    config = configparser.ConfigParser()
    config.read('config.ini')

    input_data = config['PATH']['path_original_file']
    path2garbage = config['PATH']['path2garbage'] 
    blacklist = config['PATH']['path2blacklist'] 
    path2metadata = config['PATH']['path_metadata_new'] 
    
    metadata = pd.read_csv(path2metadata, sep = ',', quotechar = '"',  encoding = 'utf-8', low_memory=False)

    list_of_json_files = os.listdir(input_data)

    """ 
    ## if in iterate_script.py we use os.system(f'python3 {my_file}.py {lang} {new_lst}') we must transform to a string
    list_of_json_files = ','.join(list_of_json.split(",")
    print(list_of_json_files)
    """


    lst_of_blacklist = []
    lst_of_str_blacklist = []
    count = 0
    
    #list_of_json_files= ["d0c6b0c2d387baae89eb2898969913218b3bedff.json"]
    #list_of_json_files = ["PMC6800015.xml.json","PMC7211516.xml.json","0d48ac42e61b7dec92e127839151f0f92d2dfa54.json","00c8546ba285b32184e67eec618d4f4caadcfe17.json","PMC6800308.xml.json","PMC7211559.xml.json","ffed5d2a31a0c1a0db11905fe378e7735b6d70ca.json","646cf3da31ec468a64e1f1710e9573e94586aae5.json","PMC6800459.xml.json","PMC7211563.xml.json","ffef8194e52de95fe345db7dd12fe3185d786978.json","646d3092d14896e26c741391f0b5fe5b724f4a39.json","PMC6800557.xml.json","PMC7211566.xml.json","ffeffafec5c5db2f5bd2472bac2f7c5cabe13557.json","646e1563272926efc0d7100555511eb7b4b98aa6.json","PMC6802222.xml.json","PMC7211568.xml.json","fff1300883abf1228c0dde1c7adfdce76d921ce2.json"]
    for file in list_of_json_files:

        # check valid json file, i.e. contains values
        try:
            j_file_original = open_json_file(path=input_data, file=file.split('.')[0])
            #print(j_file_original)
        except Exception as e:
            print(f'Original json file does not exist. Error message {e}')
            lst_of_str_blacklist.append(file.split('.')[0])
            lst_of_blacklist.append(file)
            continue   

        # check title 
        title = unidecode.unidecode(get_title_json(j_file_original)) 
        if len(title)==0:
            continue
        
        # for each article check language, by default english is choosen
        # if article is written in different language, the paper_id will be 
        # in a blacklist text file, and the json will be moved from initial folder
        if not check_language(data=title, language= config['LANG']['lang']):

            print('No english: ', j_file_original['paper_id'], ' + ', title)
            lst_of_str_blacklist.append(file.split('.')[0])
            lst_of_blacklist.append(file)
            continue

        # for each article, we will find valid authors or even if the articles contains
        # information about them. If not the paper_id will be inserted in a blacklist text 
        # file, and the json will be moved from initial folder

        # check if json file contains authors, otherwise try to find them in metadata.csv
        # if value remains null them put this article in the blacklist file
        if len(get_authors_names(data=j_file_original, csv=metadata))==0:
            print(f'Authors list does not exist.')
            lst_of_str_blacklist.append(file.split('.')[0])
            lst_of_blacklist.append(file)
            continue  

        # Get date (year)
        try:
            if len(get_date(data=j_file_original['paper_id'], csv=metadata))==0:
                lst_of_str_blacklist.append(file.split('.')[0])
                lst_of_blacklist.append(file)
                continue  
            # print(publish_date)
        except Exception as e:
            print(f'Date does not exist. Error message {e}')
                         
    try:
        if not os.path.exists(path2garbage):
            os.makedirs(path2garbage)
    except OSError as error:
        print(error)

    # # send non-valid articles to another directory
    for file in lst_of_blacklist: 
        if os.path.isfile(os.path.join(input_data, file)): 
            shutil.move(os.path.join(input_data, file), os.path.join(path2garbage, file))

    set_blacklist(file=blacklist, line=lst_of_str_blacklist)        

# ---------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    #main(lang, list_of_json)    
    main()