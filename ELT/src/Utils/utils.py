###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 29 Apr 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 01 Oct 2021 - News functions were used (after line 100)      #      
#   (author: matilde.pato@gmail.com  )                                        # 
#                                                                             #   
#                                                                             #  
###############################################################################

import os
import shutil
from pathlib import Path
from typing import Iterable


def new_file(file):

    try:
        if not os.path.isfile(file):
            f = open(file, 'w')
    except OSError as error:
        print(error)


def new_folder(path: str):
    """
    Create a new folder, if not exists; Nothing otherwise.

    :param path: The path where the folder will be created
    """
    os.makedirs(path, exist_ok=True)


def transfer_file(lst_files: list, src: str, dst: str, flag: str) -> None:
    """
    Copy or move files from one folder to another, based on list of files.

    :param  lst_files: list of file names to copy or move
    :param  src: path of source
    :param  dst: path of destination
    :param  flag: constant value 'copy' or 'move'
    :return None

    E.g.
    File copied successfully.
    ../data/document_parses/pdf_json/3e7204f7030a9956a95b58d84d283d85229cc117.json
    """

    new_folder(dst)

    print(f'{flag} files!')
    for file in lst_files:
        if os.path.isfile(os.path.join(src, file)):
            try:
                if flag == 'copy':
                    shutil.copy(os.path.join(src, file), os.path.join(dst, file))
                elif flag == 'move':
                    shutil.move(os.path.join(src, file), os.path.join(dst, file))
            # For other errors
            except Exception as e:
                print(f"Error occurred while {flag} file.")
                print(e)
        else:
            print("file does not exist: file")
    print(f'End of {flag} successfully.')


def save_metadata(filename: str, line: str) -> None:
    """
    This function will save all metadata about the process in txt file
    :param  filename: name of txt file
            line: all content
    :param line: the information to save
    :return none
    """
    dir_name: str = os.path.dirname(filename)
    if not os.path.exists(dir_name):
        os.makedirs(dir_name, exist_ok=True)

    new_file(filename)
    with open(filename, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n')
        f.write('------------------------------------------------------' + '\n' + content)
        f.close()


def save_to_file_lines(lines: Iterable, file: str) -> None:
    with open(file, 'w', encoding='utf-8') as fp:
        for line in lines:
            fp.write(f'{line}\n')


def load_from_file_lines(file: str) -> list:
    with open(file, 'r', encoding='utf-8') as fp:
        return [
            line.rstrip('\n') for line in fp.readlines()
        ]


"""
def custom_tokenizer(nlp):
    infix_re = re.compile(r'''[.\,\?\:\;\...\‘\’\`\“\”\"\'~]''')
    prefix_re = compile_prefix_regex(nlp.Defaults.prefixes)
    suffix_re = compile_suffix_regex(nlp.Defaults.suffixes)

    return Tokenizer(nlp.vocab, prefix_search=prefix_re.search,
                                suffix_search=suffix_re.search,
                                infix_finditer=infix_re.finditer,
                                token_match=None)

# --------------------------------------------------------------------------- #
"""
'''
def new_folder(path):

    try:
        if not os.path.exists(path):
            os.makedirs(path)
    except OSError as error:
        print(error)
        
# --------------------------------------------------------------------------- #

def new_file(file):

    try:
        if not os.path.isfile(file):
            f = open(file, 'w')
    except OSError as error:
        print(error)  

# --------------------------------------------------------------------------- #

def get_blacklist(file):
    """
    Return all articles to be removed, due some errors found there
    :param  file: name of file where the list will be found
    :return lst_articles: list of articles
    """

    lst_articles = []
    if os.path.isfile(file):
        with open(file, 'r') as f:
            black_list = [content for content in f.readlines()]
        lst_articles.extend(black_list) 
        f.close()
    return  lst_articles       

# --------------------------------------------------------------------------- #

def set_blacklist(file, line):
    """
    This function receives the article to and saves them in the
    blacklist file. The backlist contains all invalid articles, such
    as non-authors, non-entities, and others
    :param  filename: name of txt file
            line: all content
    :return none        
    """

    new_folder(os.path.dirname(file))
    new_file(file)
    with open(file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n')
        f.write(content)
        f.close()

# --------------------------------------------------------------------------- #

def save_final_data(data, path):
    """
    Save data to csv file
    :param data: pandas Dataframe with columns <user, item, rating, ...>
    :param path: path to the csv file
    :return
    """
    if not os.path.exists(os.path.dirname(path)):
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)   
    data.to_csv(path, index=False, header=False)
    
# --------------------------------------------------------------------------- #

def save_metadata(file, line):
    """
    This function will save all metadata about the process in txt file
    :param  filename: name of txt file
            line: all content
    :return none        
    """

    if not os.path.exists(os.path.dirname(file)):
        Path(os.path.dirname(file)).mkdir(parents=True, exist_ok=True) 
        
    new_file(file)    
    with open(file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n')
        f.write('------------------------------------------------------' + '\n' + content)
        f.close()

# ---------------------------------------------------------------------------------------- # 

def transfer_file(lst_files, src, dst, flag):
    """
    Copy or move files from one folder to another, based on list of files. 
    The source folder will be deleted at the end

    :param  lst_files: list of file names to copy or move
            src: path of source
            dst: path of destination
            flag: constant value 'copy' or 'move'
    :return none        
    
    E.g. 
    File copied successfully.
    ../data/document_parses/pdf_json/3e7204f7030a9956a95b58d84d283d85229cc117.json
    """
   
    new_folder(dst)

    print(f'{flag} files!')
    for file in lst_files:
        if os.path.isfile(os.path.join(src, file)):
            #print(os.path.isfile(os.path.join(src, file)))  
            try:
                if flag == 'copy':
                    shutil.copy(os.path.join(src,file), os.path.join(dst,file))
                elif flag == 'move':
                    shutil.move(os.path.join(src, file), os.path.join(dst, file)) 
                    #shutil.move(os.path.join(src, file.replace(str,'')), os.path.join(dst, file.replace(str,'')))    
            # For other errors
            except:
                print(f"Error occurred while {flag} file.")
        else:
            print("file does not exist: file")
    print(f'End of {flag} successfully.")')    

# --------------------------------------------------------------------------- #

def transfer_metadata(file, src, dst, flag):
    """
    Copy or move metadata from one folder to another

    :param  file: single file
            src: path of source
            dst: path of destination
            flag: constant value 'copy' or 'move'
    :return none        
    
    """    
    new_folder(dst)

    print(f'{flag} file!')
    if os.path.isfile(os.path.join(src, file)): 
        print(os.path.isfile(os.path.join(src, file)))  
        try:
            if flag == 'copy':
                shutil.copy(os.path.join(src,file), os.path.join(dst,file))
                print(f'End of {flag} successfully.")')     
            elif flag == 'move':
                shutil.move(os.path.join(src, file), os.path.join(dst, file))
                #shutil.move(os.path.join(src, filename.replace(str,'')), os.path.join(dst, filename.replace(str,''))) 
                print(f'End of {flag} successfully.")')        
        # For other errors
        except:
            print("Error occurred while copying file.")
    else:
        print("file does not exist: filename")
        
# ---------------------------------------------------------------------------------------- #

def valid_names(data):
    """
    This function will validate names of a person, and return them if any 
    Name must include surname  
    :param  data: list with all authors names in the article
    :return list with valid name
    """
    nlp = spacy.load("xx_ent_wiki_sm")
    nlp.tokenizer = custom_tokenizer(nlp)
    
    #names = '; '.join([str(item) for item in data])
    names = '; '.join([" ".join(str(item).split()) for item in data])
    if len(data)==1:
        return [ str(nlp(unidecode.unidecode(names))) ]
    
    # prevent redundant replacements of single-space with single-space
    #doc = nlp(re.sub('\s{2,}', ' ',unidecode.unidecode( names ))) 
    doc = nlp( unidecode.unidecode(names) )
    #print( [ (X.text, X.label_) for X in doc.ents ] )#if X.label_ == 'PER'
    return [(X.text) for X in doc.ents if X.label_ == 'PER' and hasSpaceAndAlpha(X.text)]

# ---------------------------------------------------------------------------------------- #
# aux functions

def hasSpaceAndAlpha(string):
    return any(char.isalpha() for char in string) and any(char.isspace() for char in string) and hasDashCharacter(string) and \
         all(char.isalpha() or char.isspace() or hasDashCharacter(string) for char in string)

def hasDashCharacter(string):
    return bool(re.match("^[A-Za-z-]", string))
'''


def valid_names():
    return None
