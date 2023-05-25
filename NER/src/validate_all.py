###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 29 May 2022                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1:       #      
#   (author:  )                                        # 
#                                                                             #   
#                                                                             #  
###############################################################################
#
# This module this module allows you to verify that all documents have been properly
# cataloged. Otherwise, the cataloged documents will (temporarily) move to a new 
# folder, and then it is recommended to run mer_entities_drugbank.py or mer_entities_batch.pt.
#
#  1. python3 validate_all.py

import os
import shutil
import pandas as pd
import numpy as np
import configparser


def main():
    config = configparser.ConfigParser()
    config.read('configurations.ini')

    path = config['PATH']['path_to_original_json']
    path_new = '/data/comm_use_subset_temp/'
    path_e = config['PATH']['path_to_entities_json']

    #
    # 1st step: move all docs non-cataloged to a temporary folder
    # and, after run python3 mer_entities_drugbank.py or python3 mer_entities_batch.py
    # finally, comment all this lines before 2nd step
    #

    if not os.path.exists(path_new):
        os.makedirs(path_new)

    # list all files in comm_use_subset and store in dataframe
    list_of_files = os.listdir(path)
    df_files = pd.DataFrame(np.array(list_of_files), columns=['titles'])
    df_files = df_files['titles'].str.replace(".json|.xml.json", "")
    # print(df_files)

    # list all files in comm_use_subset_entities and store in dataframe
    list_of_entities = os.listdir(path_e)
    df_ent = pd.DataFrame(np.array(list_of_entities), columns=['titles'])
    df_ent = df_ent['titles'].str.replace("_entities.json", "")
    # print('2: ', len(df_ent))

    list_of_ent = df_ent.values.tolist()
    df_with_ent = df_files[df_files.isin(list_of_ent)]

    for f in df_with_ent.values.tolist():
        f = (f + '.xml.json') if f.startswith('PMC') else (f + '.json')
        shutil.move(os.path.join(path, f),
                    os.path.join(path_new, f))

    # end of step 1

    os.system('python3 python3 mer_entities_batch.py')

    # 2nd step: Uncomment at the end, transfer files and remove the temp folder 

    for f in os.listdir(path_new):
        # f = (f + '.xml.json') if f.startswith('PMC') else (f + '.json')
        shutil.move(os.path.join(path_new, f),
                    os.path.join(path, f))
    os.remove(path_new)


if __name__ == '__main__':
    main()
