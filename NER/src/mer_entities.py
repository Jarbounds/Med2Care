#######################################################################################
#                                                                                     #
# @authors: Matilde Pato, Nuno Datia and Renato Marcelo (Adapted from André Lamurias) #
# @date: 21 Dec 2022                                                                  #
# @version: 1.0                                                                       #
#                                                                                     #
#######################################################################################
#
# This module extracts entities present in the retrieved documents, and it is
# based on python implementation of MER: Entity Extraction (Named Entity Recognition + Linking)
#
# Run:
# python3 mer_entities.py 

import os
import json
import re
from datetime import datetime
from utils.utils import save_metadata, create_output_folder
from utils.utils2mer import \
    merpy, \
    update_mer, \
    items_in_blacklist, \
    resolve_known_missing_terms, \
    replace_problematic_chars
from utils.json_member_utils import get_member_recursive, get_member_lexicon_relations, json_entities


def find_entities(doc: str, lexicons: list):
    output_entities = []

    doc = re.sub(r"[^A-Za-z0-9 ]{2,}", repl, doc)

    doc_results = []
    for lexicon in lexicons:
        doc = items_in_blacklist(doc, lexicon)
        doc = replace_problematic_chars(doc)
        doc = resolve_known_missing_terms(doc, lexicon)
        doc_results += merpy.get_entities(doc, lexicon)

    for e in doc_results:
        if len(e) > 2:
            entity = [int(e[0]), int(e[1]), e[2]]
            if len(e) > 3:  # URI
                entity.append(e[3])
            to_add: bool = True
            for output_entity in output_entities:
                entity_name = entity[2]
                entity_url = ''
                if len(entity) > 3:
                    entity_url = entity[3]
                if output_entity[2] == entity_name:
                    to_add = False
                    break
                if len(output_entity) > 3 and len(entity) > 3 and output_entity[3] == entity_url:
                    to_add = False
                    break
            if to_add:
                output_entities.append(entity)
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

    member_lexicons: dict = get_member_lexicon_relations()

    for member in new_doc.keys():
        value: str = get_member_recursive(doc, member)
        current_member_lexicons: list = member_lexicons.get(member, [])
        if len(current_member_lexicons) == 0:
            new_doc[member] = value
        else:
            l_value: list = find_entities(value, current_member_lexicons)
            if len(l_value) == 0:
                new_doc[member] = value
            else:
                new_doc[member] = l_value

    # Serializing json 
    json_object = json.dumps(new_doc, indent=4, ensure_ascii=False)

    output_file = f'{output_dir}/{doc_file.split("/")[-1].split(".")[0]}_entities.json'

    with open(output_file, "w", encoding='utf-8') as f_out:
        f_out.write(json_object)
        f_out.close()


def repl(m):
    # replace all matches with "a"
    return "" * len(m.group())


def main():
    """
    input:
    {
        "medicine_id": "2d2f07c15dad39e56224c9a1365e12fbd7db29da",
        "emc_id": "8048",
        "metadata": {
            "name": "Epivir 150 mg film-coated tablets",
            "composition": "Epivir 150 mg film coated tablets Each film...",
            ...
        },
        "revision_date": "2021-08-09"
    ...
    }
    output:
    {
        "medicine_id": "0a5b8413397c8212cd6582383a0922ccb7b77535",
        ...
    }
    """

    import time
    import multiprocessing
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

    parameters_list: list = [
        (input_dir + "/" + d, active_lexicons, output_dir, path_to_blacklist)
        for d in os.listdir(input_dir)
    ]

    # for parameters in parameters_list:
    #     doc_entities.append(
    #         process_doc(*parameters)
    #     )

    with multiprocessing.Pool(processes=1) as pool:
        doc_entities = pool.starmap(
            process_doc,
            parameters_list,
        )
        time.sleep(0.5)
        pool.close()
        pool.join()

    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\n\
                No. medicines: {len(doc_entities)}\n\
                '
    save_metadata(file=config['PATH']['path_to_info'], metadata=metadata)
    print("FINISHED!")


if __name__ == '__main__':
    main()
