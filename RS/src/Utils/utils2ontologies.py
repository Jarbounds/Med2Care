###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 31 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#  (Adapted from Márcia Barros, Pedro Ruas, Diana Sousa)                      #  
# @last update:                                                               #  
#   version 1.1:                                                              #      
#   (author:   )                                                              # 
#                                                                             #   
#                                                                             #  
###############################################################################

import os
import urllib.request
import requests
import shutil
from pathlib import Path

from myconfiguration import MyConfiguration as cfg

import rdflib
from rdflib import URIRef

# --------------------------------------------------------------------------- #

def get_owl(url, path):
    '''
    Download owl file and save it in a pre-defined folder. If <path>
    does not exist script will create it in current working directory and save 
    file in it
    This is written specially to large file. The chunk size that we want to 
    download at a time is specified
    :param url: url of the ontology
           path: folder where owl will be save 
    '''
    # create folder if it does not exist
    if not os.path.exists(path):
        os.makedirs(path)  

    filename = url.split('/')[-1].replace(" ", "_")  # be careful with file names
    file_path = os.path.join(path, filename)
    
    print(f'Downloading ... {filename}')

    if url.startswith('ftp'):
        with urllib.request.urlopen(url) as r:
            with open(file_path, 'wb') as f:
                shutil.copyfileobj(r, f)
    else:
        r = requests.get(url, stream = True)
        if r.ok:
            with open(file_path, "wb") as owl:
                for chunk in r.iter_content(chunk_size = 1024 * 8):
                    if chunk:
                        owl.write(chunk)
                        owl.flush()
                        os.fsync(owl.fileno())
        else:  # HTTP status code 4XX/5XX
            print("Download failed: status code {}\n{}".format(r.status_code, r.text))

# --------------------------------------------------------------------------- #

def loading_items(is_chebi, is_do, is_go, is_hp):
    '''
    Loading ontologies to get the entities label
    :param is_chebi, is_do, is_go, is_hp: boolean to represent which ontologies must be
        loading  
    :return chebi, do, go, hp: owl graph        
    '''
    arg = cfg.getInstance()
    
    # if chebi_lite.owl does not exists
    if (not os.path.exists(arg.path_chebi) and is_chebi):
        url = "http://purl.obolibrary.org/obo/chebi/chebi_lite.owl"#"ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.owl"
        get_owl(url, path=os.path.dirname(arg.path_chebi))

    # if doid.owl does not exists
    if (not os.path.exists(arg.path_do) and is_do):
        url = " http://purl.obolibrary.org/obo/doid.owl"
        get_owl(url, path=os.path.dirname(arg.path_do))  
    
    # if go.owl does not exists
    if (not os.path.exists(arg.path_go) and is_go):
        url = "http://purl.obolibrary.org/obo/go.owl"
        get_owl(url, path=os.path.dirname(arg.path_go))

    # if hp.owl does not exists
    if (not os.path.exists(arg.path_hp) and is_hp):
        url = "http://purl.obolibrary.org/obo/hp.owl"
        get_owl(url, path=os.path.dirname(arg.path_hp))
    
    # # if taxon.owl does not exists
    # if (not path.exists(arg.path_taxon) and is_taxon):
    #     url = "http://purl.obolibrary.org/obo/ncbitaxon.owl"
    #     get_owl(url, os.path.dirname(arg.path_taxon))

    # # if cido.owl does not exists
    # if (not path.exists(arg.path_cido) and is_cido):
    #     url = "https://raw.githubusercontent.com/CIDO-ontology/cido/master/src/ontology/cido.owl"
    #     get_owl(url, os.path.dirname(arg.path_cido))

    # create a Graph
    chebi = do = go = hp = rdflib.Graph()
    if is_chebi:
        print('Loading ... chebi')    
        chebi = load_ontology(path=arg.path_chebi)
    if is_do:
        print('Loading ... doid')
        do = load_ontology(path=arg.path_do)
    if is_go:
        print('Loading ... go')
        go = load_ontology(path=arg.path_go)  
    if is_hp:
        print('Loading ... hp')
        hp = load_ontology(path=arg.path_hp)     
    
    return chebi, do, go, hp

# --------------------------------------------------------------------------- #

def load_ontology(path):

    g = rdflib.Graph()
    g.load(path)
    return g

# --------------------------------------------------------------------------- #

def get_entities_labels(lst, prefix_chebi, prefix_do, prefix_go, prefix_hp):
    '''
    Get entities lables from http://purl.obolibrary.org/obo/ based on items prefix
    :param  lst: list of entities
            chebi, do, go, hp: items prefix of entities
    :return label: entities label
    '''
    label = []
    for id in lst: 

        uri = URIRef('http://purl.obolibrary.org/obo/' + id)
        if id.startswith('CHEBI'):
            lab = prefix_chebi.label(uri)
        elif id.startswith('GO'):
            lab = prefix_go.label(uri)
        elif id.startswith('HP'):
            lab = prefix_hp.label(uri)
        elif id.startswith('DO'):
            lab = prefix_do.label(uri)
        label.append(lab)
    return label