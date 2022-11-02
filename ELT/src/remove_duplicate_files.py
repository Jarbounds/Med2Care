
###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 09 Apr 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 26 May 2022 - Add config.ini file                            #    
#   (author: matilde.pato@gmail.com  )                                        #  
#                                                                             #   
#                                                                             #  
###############################################################################
#
# Find duplicates articles in pmc and non-pmc folders, and copy/move uniques to 
# another folder
#
# python3 remove_duplicate_files.py [<option>]
#  where option = 'copy' or 'move' files
#  by default = 'copy'
# version 1.1
# python3 remove_duplicate_files.py

import os.path
import sys
import pandas as pd
import numpy as np
import json
import unidecode
import configparser

from Utils.utils import  transfer_file, save_metadata
from Utils.utils2metadata import *
from Utils.utils2json import has_abstract_file, open_json_file, get_title_json, get_article_id


# --------------------------------------------------------------------------- #

def get_list_of_articles(src, index):
    '''
    Get list of all articles with ids and corresponding titles
    :param  src: path where files is
            index: constant like 'PMC' or 'PDF' 
    :return lists such as list_of_ids and list_of_titles

    '''
    list_of_articles = os.listdir(src)

    list_of_titles, list_of_ids = [], []

    for file in list_of_articles:
        if index=='PMC':
            file = file.split('.')[0]
        elif index=='PDF':    
            file = file.strip('.json')
        j_file = open_json_file(path=src, file=file)        
        title = get_title_json(j_file)
        if (index=='PMC' and len(title)>0):
            flag = True
        elif (index=='PDF' and len(title)>0 and has_abstract_file(j_file)):       
            flag = True
        else:
            flag = False    
        if flag:        
            title = unidecode.unidecode(title)
            list_of_titles.append(title)
            list_of_ids.append(get_article_id(j_file))  
    
    return list_of_ids, list_of_titles      

          
# --------------------------------------------------------------------------- #

def verify_articles_overlapping(pdf_dir, pmc_dir):
    '''
    Find all duplicate files in both folder, and return the uniques
    :param  pdf_dir: path where non-pmc files is
            pmc_dir: path where pmc files is 
    :return lists of the ids of pmc and non-pmc articles and no. of duplicates

    '''
    list_of_pdf_titles, list_of_pdf_ids = [], []
    list_of_pmc_titles, list_of_pmc_ids = [], []
    
    print("CORD-19")

    list_of_pdf_ids, list_of_pdf_titles = get_list_of_articles(src=pdf_dir, index='PDF')
    # all non-pmc articles, with abstract and title
    df_pdf = pd.DataFrame(np.array(list_of_pdf_titles), columns=['pdf_titles'])
    df_pdf['pdf_ids'] = np.array(list_of_pdf_ids)
    #print(df_pdf)

    print("PMC")
    list_of_pmc_ids, list_of_pmc_titles = get_list_of_articles(src=pmc_dir, index='PMC')
    # all pmc articles with title
    df_pmc = pd.DataFrame(np.array(list_of_pmc_titles), columns=['pmc_titles'])
    df_pmc['pmc_ids'] = np.array(list_of_pmc_ids)
    #print(df_pmc)

    print('Start')
    # pmc and other in duplicate
    # pdf_title + pdf_ids
    pdf_in_pmc = df_pdf[df_pdf.pdf_titles.isin(list_of_pmc_titles)]

    ## others articles: only non-pmc
    pdf = df_pdf[~df_pdf.pdf_titles.isin(list_of_pmc_titles)]
    ##print('pdf: ', pdf)

    # only pmc's articles
    result_pmc = df_pmc[~df_pmc.pmc_titles.isin(list_of_pdf_titles)] 

    ## df with duplicate rows removed based on pmc_titles column
    result_pmc.drop_duplicates('pmc_titles', keep='first') 
    ##print('pmc: ', result_pmc)
    ## now verify in pmc article if the corresponding pdf contains 'abstract'
    list_of_ids, list_of_title = [], []
    
    for index, row in pdf_in_pmc.iterrows():        
        j_file = open_json_file(path=pdf_dir, file=row['pdf_ids'])
        if has_abstract_file(j_file):
            # append
            list_of_ids.append(row['pdf_ids'])
            list_of_title.append(row['pdf_titles'])
           
    pmc_with_abstract = pd.DataFrame(np.array(list_of_title), columns=['pdf_titles'])
    pmc_with_abstract['pdf_ids'] = np.array(list_of_ids)
    #print('pm_w: ', pmc_with_abstract)

    result_pdf = pdf.append(pmc_with_abstract)
    # df with duplicate rows removed based on pdf_titles column
    result_pdf.drop_duplicates('pdf_titles', keep='first')
    #print(result_pdf)

    list_of_ids_pdf = result_pdf['pdf_ids'].values.tolist()
    list_of_ids_pmc = result_pmc['pmc_ids'].values.tolist()

    return len(pmc_with_abstract), list_of_ids_pdf, list_of_ids_pmc


# --------------------------------------------------------------------------- #

def main():

    '''E.g. CORD-19: cord-19_2020-05-19.tar.gz
    number of non-pmc files: 59561
    number of pmc files: 43753  

    sample of non-pmc valid
    CORD-19
                                              pdf_titles                                   pdf_ids
    0      Infection with equine infectious anemia virus ...  4d1cc919114cd1f5a24e66191a11812dca3c1062
    1      Triage tool for suspected COVID-19 patients in...  02a371b11d7168d2706312ff9f4efb9335491d06
    2      Association between passive immunity and healt...  1ece996da2419d7375b523a314c31334ad097c52
    3      Genetic grouping for the isolates of avian inf...  bf9c53277b382c09c854fed08730eff384073bdd
    4      Infectious exacerbations of chronic obstructiv...  763dfacfa897cb67df1ed94ce723b230c6bdde85
    . ..                                                  ...         ...
    [40681 rows x 2 columns]

    PMC
                                                pmc_titles     pmc_ids
    0      Receptor recognition and cross-species infecti...  PMC3840050
    1      Limited shedding of an S-InDel strain of porci...  PMC7117288
    2      Host defense function of the airway epithelium...  PMC7167170
    3      FGL2 is positively correlated with enhanced an...  PMC7075367
    4      Functional Characterization of Plasmodium falc...  PMC6057521
    . ..                                                  ...         ...
    [43753 rows x 2 columns]

    After removing duplicates, we get
    sample of non-pmc - remains the first, regarding to the pmc we remove almost 20000 articles

    PMC - only                                   pmc_titles     pmc_ids
    0      Receptor recognition and cross-species infecti...  PMC3840050
    3      FGL2 is positively correlated with enhanced an...  PMC7075367
    4      Functional Characterization of Plasmodium falc...  PMC6057521
    5           Adenoviral Vector Vaccines Antigen Transgene  PMC7150117
    6              Hamotherapie und Patient Blood Management  PMC7123155
    . ..                                                  ...         ...
    [23644 rows x 2 columns]

'''
    from datetime import datetime

    start_time = datetime.now()
    
    config = configparser.ConfigParser()
    config.read('config.ini')
   
    pdf_dir = config['PATH']['pdf_dir']
    pmc_dir = config['PATH']['pmc_dir']
    path_original_file = config['PATH']['path_original_file']
    path_to_metadata = config['PATH']['path_metadata']  
    
    print(f'number of non-pmc files: {len(os.listdir(pdf_dir))}')
    print(f'number of pmc files: {len(os.listdir(pmc_dir))}')
    
    # Find duplicates in metadata.csv and remove empty rows
    # new csv will be created without duplicates
    cleaning_csvmetadata(path_to_metadata, 'sha', '; ')

    # Find duplicates files and return a list of non-pmc and pmc ids. 
    # The number of duplicates will be count
    count_duplicate, list_of_ids_pdf, list_of_ids_pmc = verify_articles_overlapping(pdf_dir, pmc_dir)

    flag = False
    ##list of files only contains the ids, then we must add the extension
    if len(list_of_ids_pdf)>0:
        print("PDF")
        list_of_ids_pdf = [ids + '.json' for ids in list_of_ids_pdf]
        # copy or move pmc and non-pmc files to dst folder
        transfer_file(lst_files=list_of_ids_pdf, src=pdf_dir, dst=path_original_file, flag=config['TRANSFER']['option'] )
        flag = True

    if len(list_of_ids_pmc)>0:  
        print("PMC")  
        list_of_ids_pmc = [ids + '.xml.json' for ids in list_of_ids_pmc]
        # copy or move pmc and non-pmc files to dst folder
        transfer_file(lst_files=list_of_ids_pmc, src=pmc_dir, dst=path_original_file, flag=config['TRANSFER']['option'])
        flag = True
    
    """ if flag:
        transfer_csvmetadata(file=os.path.basename(new_csv_filename), src=os.path.dirname(path_to_metadata), dst=dst_dir.rsplit('/', 2)[0]+'/', flag=option)
    """
    print(f'Duration: {datetime.now() - start_time}')

    
# --------------------------------------------------------------------------- #
    ## save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Intitial data:  no. of non-pmc: {len(os.listdir(pdf_dir))} and no. of pmc: {len(os.listdir(pmc_dir))}\n\
                No. of PMC-articles transfered: {len(list_of_ids_pmc)}\n\
                No. of non-PMC-articles transfered: {len(list_of_ids_pdf)}\n\
                No. of duplicate-articles: {count_duplicate}\n\
                '

    save_metadata(file=config['PATH']['path_to_info'], line=metadata)
    
    # Remove folder and files
    #shutil.rmtree(os.getcwd()+'/'+os.path.dirname(path_to_metadata)) 
# ---------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    
    main()
