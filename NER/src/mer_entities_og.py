
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

import os
import sys
import json
import re
import multiprocessing
from collections import Counter
from itertools import chain
from datetime import datetime
import merpy
import configparser

global_entities = Counter()

from Utils.utils import create_entities_folder, save_metadata, set_blacklist
from Utils.utils2mer import *
from Utils.utils2pubmed import *

# --------------------------------------------------------------------------- #

def json_entities(original):

    entities_json = {
        "id": original["paper_id"],
        "entities": {},
        "sections": {"title": [], "abstract": [], "body": [], "captions": []},
    }
    return entities_json

# --------------------------------------------------------------------------- #

def abstract_dict(original):

    #abstract=[ { "text": a } for a in text] 
    return [ { "text" : a } for a in original] 

# --------------------------------------------------------------------------- #

def process_doc(doc_file, lexicons, output_dir, blacklist):
    """
    Open one json file with one doc, run merpy with lexicons and write results to external file
    :param doc_file: name of the document
    :param lexicons: list of the entities (ontologies)
    :param output_dir: path where documents will be saved
    :param blacklist: file where all non-valid documents are registered 
    :return doc_counter: the 10 most common list of entities
    """

    with open(doc_file, "r") as f_in:
        doc = json.load(f_in)
        
    new_doc = json_entities(original=doc)

    #
    ## Annotate the Title
    #
    # iterate through title, abtract and section
    title = doc["metadata"]["title"] 
    print('doc: ', doc["paper_id"], ' title: ', title)
    # with open(output_dir + doc_file.split("/")[-1].split(".")[0] + "_entities.json", "w") as f_out:
    #     json.dump(title, f_out, indent=4)
    
    #print('title ', title)
    if "title" in doc["metadata"]:
        new_doc["sections"]["title"] = process_multiple_docs_lexicons_sp(captions, lexicons)
        new_doc["sections"]["title"] = new_doc["sections"]["title"][0]   
    else:
        if doc["paper_id"].startswith('PMC'):
            # convert str to a dict
            try:
                print(f'Find title, now with metapub.')              
                title = get_title_by_metapub(pmcid=doc["paper_id"]) 
                print('title Meta: ', title) 
            except Exception as e: 
                    try:                    
                        print(f'Find title, now with Bio. Error message {e}') 
                        title = get_title_by_bio(pmid=get_pmid(pmcid=doc["paper_id"])) 
                        print('title Bio: ', title)  
                    except Exception as e:  
                        print(f'No title. Error message {e}')     
            new_doc["sections"]["title"] = process_multiple_docs_lexicons_sp(captions, lexicons)
            new_doc["sections"]["title"] = new_doc["sections"]["title"][0]
        else:
            print('wo title')
            set_blacklist(file=blacklist, line=doc["paper_id"])      

    #
    ## Annotate the Abstract
    #
    # #if key: 'abstract' exist in json
    if 'abstract' in doc:
        abstract = [p["text"] for p in doc["abstract"]] 
        print('abstract1: ')   
        new_doc["sections"]["abstract"] = process_multiple_docs_lexicons_sp(captions, lexicons)   
    else:
        if doc["paper_id"].startswith('PMC'):
            try:
                # convert str to a dict
                abstract= get_abstract_by_bio(pmid=get_pmid(pmcid=doc["paper_id"]))
                #abstract_dic = abstract_dict(original=abstract_str.split('. '))
                #abstract = [ p["text"] for p in abstract_dic]
                # print('abstract PMC: ', type(abstract))
                # split abstract by '.' delimeter
                new_doc["sections"]["abstract"] = process_multiple_docs_lexicons_sp(captions, lexicons)
                new_doc["sections"]["abstract"] = new_doc["sections"]["abstract"][0]
            except Exception as e: 
                print(f'Without abstract. Error: {e}')                
        else:
            new_doc["sections"]["abstract"] = []  

    #
    ## Annotate the Body text
    #        
    if 'body_text' in doc:
        body = [p["text"] for p in doc["body_text"]]
        # print(body)
        new_doc["sections"]["body"] = process_multiple_docs_lexicons_sp(captions, lexicons)
    else:
        print('body: ', title, ' + ', doc["paper_id"])
        new_doc["sections"]["body"] = [] 

    #
    ## Annotate the Ref_entries: figures and tables
    #
    if 'ref_entries' in doc:
        # ref_entries includes figures and tables
        captions = [doc["ref_entries"][p]["text"] for p in doc["ref_entries"]]
        # print(captions)
        new_doc["sections"]["captions"] = process_multiple_docs_lexicons_sp(captions, lexicons)
    else:
        print('ref_entries', title, ' + ', doc["paper_id"])
        new_doc["sections"]["captions"] = []
    
    # # count all URI
    all_uris = []
    try:
        all_uris = [e[3] for e in new_doc["sections"]["title"] if len(e) > 3]  
        all_uris += [e[3] for e in chain.from_iterable(new_doc["sections"]["abstract"]) if len(e) > 3]
        all_uris += [e[3] for e in chain.from_iterable(new_doc["sections"]["body"]) if len(e) > 3]
        all_uris += [e[3] for e in chain.from_iterable(new_doc["sections"]["captions"]) if len(e) > 3]
    except Exception as e:
        print(f'No values. Error: {e}')
    
    # # Count URIs frequencies and sort them
    doc_counter = Counter(all_uris)
    
    new_doc["entities"] = {
        k: v
        for k, v in sorted(doc_counter.items(), key=lambda item: item[1], reverse=True)
    }

    ## find the most common list of entities
    print('document: ', doc_file)
    print("top doc", doc_counter.most_common(10))
    
    # Serializing json 
    json_object = json.dumps(new_doc, indent = 4, ensure_ascii=False)   

    with open(output_dir + doc_file.split("/")[-1].split(".")[0] + "_entities.json", "w") as f_out:
        f_out.write(json_object)
        f_out.close()
      
    return doc_counter

# --------------------------------------------------------------------------- #

def repl(m):
    # replace all matches with "a"
    return "a" * len(m.group())

# --------------------------------------------------------------------------- #

def process_multiple_docs_lexicons_sp(docs, lexicons):
    """
    Iterate through list of doc directories
    :param doc_file: name of the document
    :param lexicons: list of the entities (ontologies)
    :return output_entities: dataframe with entities names
    """
    # create one empty list for each doc
    #doc_dict = {i: d for i, d in enumerate(docs)}
    
    output_entities = [[]] * len(docs)
    doc_results = []
    for idoc, doc in enumerate(docs):
        if sum(map(str.isalnum, doc)) < 5:  # must have at least 5 alnum
            print("no words", doc)
            continue  

        doc = re.sub(r"[^A-Za-z0-9 ]{2,}", repl, doc)

        #check 
        # Apply MER to the preprocessed title, abstract, ... in order to recognize 
        # entities and to link them to the concepts:
        for l in lexicons:
            doc = items_in_blacklist(doc, l)
            doc_results += merpy.get_entities(doc, l)
        
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
    
    return output_entities


# --------------------------------------------------------------------------- #

def main():

    '''E.g. CORD-19: cord-19_2020-05-19.tar.gz
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
    '''
    import time
    start_time = datetime.now()

    config = configparser.ConfigParser()
    config.read('config.ini')

    # update MER with all entities on only specified by the user
    # available entities: {"do", "go", "hpo", "chebi", "taxon", "cido"}
    active_lexicon = config['ONTO']['active_lexicons']
    # split if there is a list of entities
    if active_lexicon != 'all':
        active_lexicon = active_lexicon.replace(' ', '').split(',')
 
    if config['ONTO']['update'] == 1:
        if active_lexicon == 'all':
            update_mer(lexicon='')      
        update_mer(lexicon=active_lexicon)
    
    doc_entities = []
    
    # read the path where files are in system
    input_dir, output_dir = create_entities_folder(src=config['PATH']['path_to_original_json'])
    path_to_blacklist = config['PATH']['path2blacklist']
        
    with multiprocessing.Pool(processes=40) as pool:          
        doc_entities = pool.starmap(process_doc,
            [
                (input_dir + "/" + d, active_lexicon, output_dir, path_to_blacklist)
                for d in os.listdir(input_dir)
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
                Ontologies: {active_lexicon}\n\
                No. articles: {len(doc_entities)}\n\
                '
    save_metadata(file=config['PATH']['path_to_info'], metadata=metadata)
    print("FINISHED!")

# --------------------------------------------------------------------------- #

if __name__ == '__main__':
     main()