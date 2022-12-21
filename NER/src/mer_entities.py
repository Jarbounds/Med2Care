###############################################################################
#                                                                             #  
# @author: Matilde Pato (Adapted from André Lamurias)                         #  
# @email: matilde.pato@gmail.com                                              #
# @date: 31 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 23 May 2021
#   Imput values are defined in config.ini file                               #      
#   (author: matilde.pato@gmail.com)                                          #  
#                                                                             #   
#                                                                             #  
###############################################################################
#
# This module extracts entities present in the retrieved documents and it is 
# based on python implementation of MER: Entity Extraction (Named Entity Recognition 
# + Linking) 
#
#  1. python3 mer_entities.py <source_path> [<list of ontologies>]
# e.g. 
#   python3 mer_entities.py ../data/comm_use_subset/  
#   python3 mer_entities.py ../data/comm_use_subset/  do chebi
# version 1.1:
# python3 mer_entities.py 

import json
import re
from datetime import datetime

from Utils.utils import create_entities_folder, save_metadata, set_blacklist, create_output_folder
from Utils.utils2mer import *
from Utils.json_member_utils import get_member_recursive


# --------------------------------------------------------------------------- #


def member_lexicons(member: str) -> list:
    chebi_lexicon = 'chebi'
    disease_lexicon = 'do'
    lexicons_relation = {
        'composition': [chebi_lexicon],
        'therapeutic_indications': [disease_lexicon],
        'disease': [disease_lexicon],
        'pregnancy': [disease_lexicon],
        'machine_ops': [disease_lexicon],
        'excipients': [chebi_lexicon],
        'incompatibilities': [chebi_lexicon]
    }
    return lexicons_relation.get(member, [])


def json_entities(original):
    entities_json: dict = {
        'name': original['metadata']['name'],
        'composition': [],
        'therapeutic_indications': [],
        'disease': [],
        'pregnancy': [],
        'machine_ops': [],
        'excipients': [],
        'incompatibilities': [],
        'date': ''
    }
    return entities_json


# --------------------------------------------------------------------------- #

def abstract_dict(original):
    # abstract=[ { "text": a } for a in text]
    return [{"text": a} for a in original]


# --------------------------------------------------------------------------- #


def find_entities(doc: str, lexicons: list):
    output_entities = []

    print(lexicons)

    doc = re.sub(r"[^A-Za-z0-9 ]", repl, doc)

    doc_results = []
    for lexicon in lexicons:
        doc = items_in_blacklist(doc, lexicon)
        doc_results += merpy.get_entities(doc, lexicon)

    for e in doc_results:
        if len(e) > 2:
            entity = [int(e[0]), int(e[1]), e[2]]
            if len(e) > 3:  # URI
                entity.append(e[3])
            if entity not in output_entities:
                output_entities.append(entity)
    #print(output_entities)
    #input()
    return output_entities


def process_doc(doc_file, lexicons, output_dir, blacklist) -> None:
    """
    Open one json file with one doc, run merpy with lexicons and write results to external file
    :param doc_file: name of the document
    :param lexicons: list of the entities (ontologies)
    :param output_dir: path where documents will be saved
    :param blacklist: file where all non-valid documents are registered 
    :return doc_counter: the 10 most common list of entities
    """

    with open(doc_file, "r", encoding='utf-8') as f_in:
        doc: dict = json.load(f_in)

    new_doc: dict = json_entities(original=doc)

    print(f"doc: {doc['medicine_id']}")

    # for member in new_doc.keys():
    #     value: str = get_member_recursive(doc, member)
    #     if value:
    #         current_member_lexicons: list = member_lexicons(member)
    #         if len(current_member_lexicons) == 0:
    #             new_doc[member] = value
    #         else:
    #             l_value: list = process_multiple_doc_lexicons_sp([value], current_member_lexicons)
    #             new_doc[member] = l_value[0]
    #
    # print(new_doc)

    composition = get_member_recursive(doc, 'composition')
    therapeutic_indications = get_member_recursive(doc, 'therapeutic_indications')
    disease = get_member_recursive(doc, 'disease')
    pregnancy = get_member_recursive(doc, 'pregnancy')
    machine_ops = get_member_recursive(doc, 'machine_ops')
    excipients = get_member_recursive(doc, 'excipients')
    incompatibilities = get_member_recursive(doc, 'incompatibilities')
    revision_date = get_member_recursive(doc, 'revision_date')

    if composition:
        # print('composition')
        l_composition: list = find_entities(composition, member_lexicons('composition'))
        new_doc['composition'] = l_composition
    if therapeutic_indications:
        # print('therapeutic_indications')
        l_therapeutic_indications: list = find_entities(therapeutic_indications, member_lexicons('therapeutic_indications'))
        new_doc['therapeutic_indications'] = l_therapeutic_indications
    if disease:
        # print('disease')
        l_disease: list = find_entities(disease, member_lexicons('disease'))
        new_doc['disease'] = l_disease
    # Todo: Check pregnancy in another form
    # if pregnancy:
    #     print('pregnancy')
    #     l_pregnancy: list = find_entities(pregnancy, member_lexicons('pregnancy'))
    #     new_doc['pregnancy'] = l_pregnancy
    # Todo: Check machine_ops in another form
    # if machine_ops:
    #     print('machine_ops')
    #     l_machine_ops: list = find_entities(machine_ops, member_lexicons('machine_ops'))
    #     new_doc['machine_ops'] = l_machine_ops
    if excipients:
        # print('excipients')
        l_excipients: list = find_entities(excipients, member_lexicons('excipients'))
        new_doc['excipients'] = l_excipients
    if incompatibilities:
        # print('incompatibilities')
        l_incompatibilities: list = find_entities(incompatibilities, member_lexicons('incompatibilities'))
        new_doc['incompatibilities'] = l_incompatibilities
    if revision_date:
        # print('revision_date')
        new_doc['date'] = revision_date

    # Serializing json 
    json_object = json.dumps(new_doc, indent=4, ensure_ascii=False)

    output_file = f'{output_dir}/{doc_file.split("/")[-1].split(".")[0]}_entities.json'

    with open(output_file, "w", encoding='utf-8') as f_out:
        f_out.write(json_object)
        f_out.close()


# --------------------------------------------------------------------------- #

def repl(m):
    # replace all matches with "a"
    return " " * len(m.group())


# --------------------------------------------------------------------------- #

def process_multiple_doc_lexicons_sp(docs, lexicons):
    """
    Iterate through list of doc directories
    :param doc_file: name of the document
    :param lexicons: list of the entities (ontologies)
    :return output_entities: dataframe with entities names
    """
    # create one empty list for each doc
    # doc_dict = {i: d for i, d in enumerate(docs)}

    output_entities = [[]]
    doc_results = []
    for idoc, doc in enumerate(docs):
        if sum(map(str.isalnum, doc)) < 5:  # must have at least 5 alnum
            print("no words", doc)
            continue

        # doc = re.sub(r"[^A-Za-z0-9 ]{2,}", repl, doc)

        # check
        # Apply MER to the preprocessed title, abstract, ... in order to recognize 
        # entities and to link them to the concepts:
        for l in lexicons:
            doc = items_in_blacklist(doc, l)
            doc_results += merpy.get_entities(doc, l)

        print(f'doc_results: {doc_results}')

        for e in doc_results:
            # doc_entities = merpy.get_entities_mp(doc_dict, lex, n_cores=10)
            # for e in l_entities:
            if len(e) > 2:
                entity = [int(e[0]), int(e[1]), e[2]]
                if len(e) > 3:  # URI
                    entity.append(e[3])
                if entity not in output_entities[idoc]:
                    output_entities[idoc].append(entity)

    for i in range(len(output_entities)):
        output_entities[i] = sorted(output_entities[i])

    print(output_entities)

    input()

    return output_entities


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
    from configparser import ConfigParser

    start_time = datetime.now()

    config: ConfigParser = ConfigParser()
    config.read('config.ini')

    # update MER with all entities on only specified by the user
    # available entities: {"do", "go", "hpo", "chebi", "taxon", "cido"}
    active_lexicons = config['ONTO']['active_lexicons']
    # split if there is a list of entities
    if active_lexicons != 'all':
        active_lexicons = active_lexicons.replace(' ', '').split(',')

    if config['ONTO']['update'] == 1:
        if active_lexicons == 'all':
            update_mer(lexicon='')
        else:
            update_mer(lexicon=active_lexicons)

    doc_entities = []

    # read the path where files are in system
    input_dir: str = config['PATH']['path_to_original_json']
    output_dir: str = config['PATH']['path_to_entities_json']
    create_output_folder(output_dir)
    path_to_blacklist = config['PATH']['path2blacklist']

    i: list = [
        (input_dir + "/" + d, active_lexicons, output_dir, path_to_blacklist)
        for d in os.listdir(input_dir)
    ]

    for a in i:
        doc_entities.append(process_doc(a[0], a[1], a[2], a[3]))

    # with multiprocessing.Pool(processes=40) as pool:
    #     doc_entities = pool.starmap(
    #         process_doc,
    #         [
    #             (input_dir + "/" + d, active_lexicons, output_dir, path_to_blacklist)
    #             for d in os.listdir(input_dir)
    #         ],
    #     )
    #     time.sleep(0.5)
    #     pool.close()
    #     pool.join()

    print(len(doc_entities))

    # --------------------------------------------------------------------------- #
    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\n\
                No. articles: {len(doc_entities)}\n\
                '
    save_metadata(file=config['PATH']['path_to_info'], line=metadata)
    print("FINISHED!")


# --------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()
