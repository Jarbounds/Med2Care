###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 09 Apr 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1:                                                              #      
#   (author: )                            #  
#                                                                             #   
#                                                                             #  
###############################################################################
#
# 
import os
import sys
from pathlib import Path
import shutil
import csv
import re
import pandas as pd
import unidecode

from utils import valid_names, new_folder, hasDashCharacter

# ---------------------------------------------------------------------------------------- #

def get_authors_csvmetadata(data, ident):

    def isNaN(num):
        return num != num
    
    list_of_authors = []
    if ident.startswith('PMC'):
        id_file = 'pmcid'
    else:
        id_file = 'sha'
    
    if len(data[data[id_file] == ident].index)==0:
        return list_of_authors
    else:     
        if isNaN(data[data[id_file] == ident].authors.values[0]):
            return list_of_authors

        if ";" in data[data[id_file] == ident].authors.values[0]:
            # if exists several authors, split and put each authors in a list
            authors = data[data[id_file] == ident].authors.values[0].split(';')
        else:  
            # only one author, check if is alphabetic letters
            authors = data[data[id_file] == ident].authors.values[0].split()

        for a in authors:
            name = re.findall('.[^A-Z-]*', unidecode.unidecode(''.join(m for m in a if m.isalpha()) or hasDashCharacter(a)) )
            list_of_authors.append(name[0] + ' ' + ''.join(name[1:]))

    return valid_names(list_of_authors)

# ---------------------------------------------------------------------------------------- #

def get_pmcid_csvmetadata(csv_meta, data):
    
    pmcid = []
    if data['paper_id'].startswith('PMC'):
        pmcid = data['paper_id']
    else:    
        if len(csv_meta[csv_meta.sha == data['paper_id']].index)!=0: 
            pmcid = csv_meta[csv_meta.sha == data['paper_id']].sha.values[0]
    
    return pmcid         
 
# --------------------------------------------------------------------------- #

def cleaning_csvmetadata(path, colname, sep):
    '''
    Remove all lines where colname is empty, and transform each element of
    a list-like to a row, replicating the index values
    Save the result to a new csv file 
    :param  path: file path
            colname: name of column where we found duplicates or empty values
            sep: argument splits
    :return none        
    '''
    df = pd.read_csv(path, sep = ',', quotechar = '"',  encoding = 'utf-8', low_memory=False)
    
    # # # remove all rows with empty value, except PMC articles with pubmed_id
    #df.dropna(subset = [colname], inplace=True)
    df[colname] = df[colname].str.split(sep)
    df = df.explode(colname)
    # save result in new csv file
    df.to_csv(os.path.splitext(path)[0]+'_new.csv',index=False)
    return None

# --------------------------------------------------------------------------- #

def transfer_csvmetadata(file, src, dst, flag):
    '''
    Copy or move metadata from one folder to another

    :param  file: single file
            src: path of source
            dst: path of destination
            flag: constant value 'copy' or 'move'
    :return none        
    
    '''    
    new_folder(dst)

    print(f'{flag} file!')
    if os.path.isfile(os.path.join(src, file)): 
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