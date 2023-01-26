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

import pandas as pd
import json
import unidecode

from Utils.utils import valid_names, hasDashCharacter

# --------------------------------------------------------------------------- #

def open_json_file_pd(path, doc):
    '''
    Convert a JSON string to pandas object, and return a dataframe
    :param path: path of the directory, which needs to be explored
           doc: name of json file 
    '''
    return pd.read_json(path + doc, orient = 'index')

# --------------------------------------------------------------------------- #

def validateJSON(jsonData):
    '''
    Method to validate it as per the standard convention.
    :param  jsonData: name of json
    :return boolean
    '''
    try:
        json.loads(jsonData)
    except ValueError as err:
        return False
    return True

# --------------------------------------------------------------------------- #

def open_json_file(path, file):
    '''
    Open JSON file object and returns the json object as dictionary
    :param path: directory, which needs to be explored
           file: name of json file 
    '''
    if file.startswith('PMC'):
        ext = '.xml.json'
    else:
        ext = '.json'
    with open(path + file + ext, encoding='utf-8') as json_file:
        return json.load(json_file)

# --------------------------------------------------------------------------- #

""" def get_article_id(data):
    return data.loc['id'].values[0]  """

# --------------------------------------------------------------------------- #

def get_article_id(doc):
    '''
    Get paper id
    :param data: json file of the article
    :return: paper_id
    '''
    return doc["paper_id"]

# --------------------------------------------------------------------------- #

def get_title_json(doc):
    return doc['metadata']['title']

# ---------------------------------------------------------------------------------------- #

def get_authors_json(doc):
    '''
    Return list of valid authors names
    :param  doc: json file
    :return list with valid name (e.g. 'surname, first name')
    '''
    list_of_authors = []
    for p in doc['metadata']['authors']:
        
        if len(p['first']) == 0 or len(p['last']) == 0:
           continue
        else:
            # remove all characters except alphabets from a string to unidecode
            first = unidecode.unidecode( ''.join(m for m in p['first'] if m.isalpha() or hasDashCharacter(p['first'])) )
            #middle = unidecode.unidecode( ''.join(m for m in p['middle'] if m.isalpha()) )
            last = unidecode.unidecode( ''.join(m for m in p['last'] if m.isalpha() or hasDashCharacter(p['last'])))
            # to validade names, surname must be first
            list_of_authors.append(last + ' '+ first)      
            
    return valid_names(list_of_authors)

# ---------------------------------------------------------------------------------------- #

def has_abstract_file(doc):
    '''
    Find abstract key in file
    :param  doc: json file
    :return boolean
    '''
    if not doc['abstract']:
        return False
    return True        