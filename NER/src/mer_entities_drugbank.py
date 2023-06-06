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
# python3 mer_entities_drugbank.py

import os
import json
import re
from multiprocessing import cpu_count, Pool
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

    doc = re.sub(r"[^A-Za-z0-9 ]{2,}", "", doc)

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


def process_str_member(member, value, current_member_lexicons):
    # print(f'{member} {value} {current_member_lexicons}')
    # input("Stopped")
    entities: list = find_entities(value, current_member_lexicons)
    if len(entities) == 0:
        print(f'{member} - No entities found')
        return ''
    else:
        print(f'{member} - Entities found')
        return entities


def process_composition(composition: str, lexicons: list):
    return process_str_member('composition', composition, lexicons)


def process_therapeutic_indications(therapeutic_indications: str, lexicons: list):
    return process_str_member('therapeutic_indications', therapeutic_indications, lexicons)


def process_disease(disease: str, lexicons: list):
    return process_str_member('disease', disease, lexicons)


def process_pharmacodynamics(pharmacodynamics: str, lexicons: list):
    return process_str_member('pharmacodynamics', pharmacodynamics, lexicons)


def process_incompatibilities(incompatibilities: list, lexicons: list):
    print('Processing incompatibilities')
    new_incompatibilities = []
    for incompatibility in incompatibilities:
        description = incompatibility.get('description', '')
        entities = process_str_member('incompatibility_description', description, lexicons)
        if len(entities) != 0:
            new_incompatibilities.extend(entities)
    return new_incompatibilities


# TODO: Configure the config file to have a map doc_field -> lexicons
def process_doc(doc_file, lexicons, output_dir, blacklist) -> None:
    """
    Open one json file with one doc, run merpy with lexicons and write results to external file
    :param doc_file: name of the document
    :param lexicons: list of the entities (ontologies)
    :param output_dir: path where documents will be saved
    :param blacklist: file where all non-valid documents are registered 
    :return doc_counter: the 10 most common list of entities
    """
    doc: dict = {}
    with open(doc_file, "r", encoding='utf-8') as f_in:
        try:
            doc: dict = json.load(f_in)
        except Exception as e:
            print(f'ERROR WITH {doc_file}')
            print(e)

    if not doc:
        print("There is no processing for this json, returning")

    new_doc: dict = json_entities(original=doc)

    print('=' * 36)
    print(f"doc: {doc['medicine_id']}")

    member_lexicons: dict = get_member_lexicon_relations()

    composition_lexicons = member_lexicons['composition']
    therapeutic_indications_lexicons = member_lexicons['therapeutic_indications']
    disease_lexicons = member_lexicons['disease']
    pharmacodynamics_lexicons = member_lexicons['pharmacodynamics']
    incompatibilities_lexicons = member_lexicons['incompatibilities']

    composition = get_member_recursive(doc, 'composition')
    therapeutic_indications = get_member_recursive(doc, 'therapeutic_indications')
    disease = get_member_recursive(doc, 'disease')
    pharmacodynamics = get_member_recursive(doc, 'pharmacodynamics')
    incompatibilities = get_member_recursive(doc, 'incompatibilities')

    composition_entities = process_composition(composition, composition_lexicons)
    therapeutic_indications_entities = process_therapeutic_indications(
        therapeutic_indications, therapeutic_indications_lexicons
    )
    disease_entities = process_disease(disease, disease_lexicons)
    pharmacodynamics_entities = process_pharmacodynamics(pharmacodynamics, pharmacodynamics_lexicons)
    incompatibilities_entities = process_incompatibilities(incompatibilities, incompatibilities_lexicons)

    new_doc['composition'] = composition_entities
    new_doc['therapeutic_indications'] = therapeutic_indications_entities
    new_doc['disease'] = disease_entities
    new_doc['pharmacodynamics'] = pharmacodynamics_entities
    new_doc['incompatibilities'] = incompatibilities_entities

    # Serializing json
    json_object = json.dumps(new_doc, indent=4, ensure_ascii=False)

    output_file = f'{output_dir}/{doc_file.split("/")[-1].split(".")[0]}_entities.json'

    with open(output_file, "w", encoding='utf-8') as f_out:
        f_out.write(json_object)

    print('=' * 36)


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
    config.read('../configurations/configurations.ini')

    # update MER with all entities on only specified by the user
    # available entities: {"do", "go", "hpo", "chebi", "taxon", "cido"}
    active_lexicons = config['ONTO']['active_lexicons']
    # split if there is a list of entities
    if active_lexicons != 'all':
        active_lexicons = active_lexicons.replace(' ', '').split(',')

    if config['ONTO']['update'] == '1':
        if active_lexicons == 'all':
            update_mer(lexicon_name_list='')
        else:
            update_mer(lexicon_name_list=active_lexicons)

    doc_entities = []

    # read the path where files are in system
    input_dir: str = config['PATH']['path_to_original_json']
    output_dir: str = config['PATH']['path_to_entities_json']
    create_output_folder(output_dir)
    path_to_blacklist = config['PATH']['path2blacklist']

    fi = [
        ''.join(file.split('_entities')) for file in os.listdir('../data/comm_use_subset_entities')
    ]

    parameters_list: list = [
        (input_dir + "/" + d, active_lexicons, output_dir, path_to_blacklist)
        for d in os.listdir(input_dir) if d not in fi
    ]

    if config['MULTITHREAD']['active'] == '1':
        with Pool(processes=cpu_count()) as pool:
            doc_entities = pool.starmap(
                process_doc,
                parameters_list,
            )
            time.sleep(0.5)
    else:
        for parameters in parameters_list:
            doc_entities.append(
                process_doc(*parameters)
            )

    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n\
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\n\
                No. medicines: {len(doc_entities)}\n\
                '
    save_metadata(file=config['PATH']['path_to_info'], metadata=metadata)
    print("FINISHED!")


if __name__ == '__main__':
    main()
