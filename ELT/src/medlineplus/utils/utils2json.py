###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 31 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#  (Adapted from Márcia Barros, Pedro Ruas, Diana Sousa)                      #  
# @last update:                                                               #  
#   version 1.1: 01 Oct 2021 - Update one function  (after line 115)          #      
#   (author: matilde.pato@gmail.com  )                                        # 
#                                                                             #   
#                                                                             #  
###############################################################################

import json
import os
import jsonpickle


def read_json_file(path: str, file: str) -> dict:
    """
    Open JSON file object and returns the json object as dictionary
    :param path: directory containing the file
    :param file: name of json file
    """
    to_open: str = file
    if not file.endswith('.json'):
        to_open = f'{file}.json'

    with open(os.path.join(path, to_open), encoding='utf-8') as json_file:
        return json.load(json_file)


def write_json_file(path: str, file: str, contents: dict) -> None:
    """
    Write JSON contents (as dictionary) to a file
    :param path: directory where to save the file
    :param file: name of the file to store the contents
    :param contents: the file contents
    """
    if not os.path.isdir(path):
        print('Path is not a directory')
        return

    with open(os.path.join(path, file), 'w', encoding='utf-8') as json_file:
        json_file.write(jsonpickle.encode(contents, unpicklable=False, indent=4))


def get_member_recursive(data: dict, member: str) -> str:
    if member in data:
        return data[member]
    for key in data.keys():
        item = data[key]
        if isinstance(item, dict):
            value = get_member_recursive(item, member)
            if value:
                return value
    return ''


def set_member_recursive(data: dict, member: str, value: str):
    if member in data:
        data[member] = value
    for key in data.keys():
        item = data[key]
        if isinstance(item, dict):
            set_member_recursive(item, member, value)


def get_medicine_id(data: dict) -> str:
    return data['medicine_id']


def get_emc_id(data: dict) -> str:
    return data['emc_id']


def get_revision_date(data: dict) -> str:
    return data['metadata']['revision_date']


def set_revision_date(data: dict, value: str) -> dict:
    data['metadata']['revision_date'] = value
    return data
