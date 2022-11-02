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

import re
import unidecode

from Utils.utils import valid_names, hasDashCharacter

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
 
