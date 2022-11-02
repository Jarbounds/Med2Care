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

def get_authors_csvmetadata(csv, ident):
    '''
    Return list of valid authors names
    :param  csv: cvs file with metadata (one column contains the name of authors)
    :param ident: id of the article given in get_article_id() function
    :return list with valid name (e.g. 'surname, first name')
    '''

    def isNaN(num):
        return num != num
    
    list_of_authors = []
    if ident.startswith('PMC'):
        id_file = 'pmcid'
    else:
        id_file = 'sha'
    if len(csv[csv[id_file] == ident].index)==0:
        return list_of_authors
    else:     
        if isNaN(csv[csv[id_file] == ident].authors.values[0]):
            return list_of_authors

        if ";" in csv[csv[id_file] == ident].authors.values[0]:
            # if exists several authors, split and put each authors in a list
            authors = csv[csv[id_file] == ident].authors.values[0].split(';')
        else:  
            # only one author, check if is alphabetic letters
            authors = csv[csv[id_file] == ident].authors.values[0].split()

        for a in authors:
            name = re.findall('.[^A-Z-]*', unidecode.unidecode(''.join(m for m in a if m.isalpha()) or hasDashCharacter(a)) )
            list_of_authors.append(name[0] + ' ' + ''.join(name[1:]))

    return valid_names(list_of_authors)

# ---------------------------------------------------------------------------------------- #

def get_pmcid_csvmetadata(csv, ident):
    '''
    Return pmcid value of the document from csv metadata file
    :param  csv: cvs file with metadata (one column contains the name of authors)
    :param ident: id of the article given in get_article_id() function
    :return list with valid name (e.g. 'surname, first name')
    '''
    pmcid = []
    if ident.startswith('PMC'):
        pmcid = ident
    else:    
        if len(csv[csv.sha == ident].index)!=0: 
            pmcid = csv[csv.sha == ident].sha.values[0]
    return pmcid         
 
