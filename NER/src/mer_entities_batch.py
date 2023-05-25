###############################################################################
#                                                                             #  
# @author: Matilde Pato (Adapted from André Lamurias)                         #  
# @email: matilde.pato@gmail.com                                              #
# @date: 26 Apr 2022                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 23 May 2022    
#   Imput values are defined in configurations.ini file                               #
#   (author: matilde.pato@gmail.com)                                          #  
#                                                                             #   
#                                                                             #  
###############################################################################
#
# This module extracts entities present in the retrieved documents and it is 
# based on python implementation of MER: Entity Extraction (Named Entity Recognition 
# + Linking) 
#
#  1. python3 mer_entities_batch.py <source_path> [<list of ontologies>]
# e.g. 
#   python3 mer_entities_batch.py ../data/comm_use_subset/  
#   python3 mer_entities_batch.py ../data/comm_use_subset/  do chebi
# version 1.1:
# python3 mer_entities_batch.py 

import shutil
import multiprocessing
import configparser
import tempfile

from collections import Counter
from datetime import datetime
from utils.utils import create_entities_folder, save_metadata
from utils.utils2mer import *
from mer_entities_drugbank import process_doc

global_entities = Counter()


# --------------------------------------------------------------------------- #

def main():
    """E.g. CORD-19: cord-19_2020-05-19.tar.gz
    input:
    {"paper_id": "0a00a6df208e068e7aa369fb94641434ea0e6070",
        "metadata": {
            "title": "BMC Genomics Novel genome polymorphisms in BCG vaccine strains and impact on efficacy",
            "authors":
            ...}
        "abstract": [{
            "text": "Bacille Calmette-Gurin (BCG) is an attenuated strain of Mycobacterium bovis currently used (...)
    ...
    }
    output:
    {
    "id": "0a5b8413397c8212cd6582383a0922ccb7b77535",
    "entities": {
        "http://purl.obolibrary.org/obo/DOID_8469": 972,
        "http://purl.obolibrary.org/obo/DOID_552": 347,
        "http://purl.obolibrary.org/obo/DOID_934": 170,
        "http://purl.obolibrary.org/obo/CHEBI_50858": 168,
    ...
                    [
                        344,
                        352,
                        "neoplasm",
                        "http://purl.obolibrary.org/obo/DOID_14566"
                    ]
                ]
            ]
        }
    }
    """
    import time
    start_time = datetime.now()

    config = configparser.ConfigParser()
    config.read('configurations.ini')
    splited_size = int(config['SAMPLE']['splitedSize'])

    # update MER with all entities on only specified by the user
    # available entities: {"do", "go", "hpo", "chebi", "taxon", "cido"}
    active_lexicons = config['ONTO']['active_lexicons']
    # split if there is a list of entities
    if active_lexicons != 'all':
        active_lexicons = active_lexicons.replace(' ', '').split(',')

    if config['ONTO']['update'] == '1':
        if active_lexicons == 'all':
            update_mer(lexicon_name_list='')
        update_mer(lexicon_name_list=active_lexicons)

    doc_entities = []

    # read the path where files are in system
    input_dir, output_dir = create_entities_folder(src=config['PATH']['path_to_original_json'])

    list_of_json_files = os.listdir(input_dir)
    list_of_lists = [list_of_json_files[i: i + splited_size] for i in range(0, len(list_of_json_files), splited_size)]

    for lst in list_of_lists:
        new_lst = ','.join(lst)

        temp_dir = tempfile.TemporaryDirectory()
        for d in new_lst.split(","):
            shutil.copy(os.path.join(input_dir, d), os.path.join(temp_dir.name, d))

        with multiprocessing.Pool(processes=50) as pool:
            doc_entities = pool.starmap(
                process_doc,
                [
                    (temp_dir.name + "/" + d, active_lexicons, output_dir)
                    for d in os.listdir(temp_dir.name)
                ],
            )
            time.sleep(0.5)
            pool.close()
            pool.join()

        for entities in doc_entities:
            global_entities.update(entities)

        print(len(doc_entities))
        print("global top", global_entities.most_common(10))
        print("total", sum(global_entities.values()))

    # --------------------------------------------------------------------------- #
    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\n\
                No. articles: {len(doc_entities)}\n\
                '
    save_metadata(file=config['PATH']['path_to_info'], metadata=metadata)


# --------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()
