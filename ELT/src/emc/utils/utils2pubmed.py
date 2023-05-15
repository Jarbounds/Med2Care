###############################################################################
#                                                                             #  
# @author: Matilde Pato (Adapted from André Lamurias)                         #  
# @email: matilde.pato@gmail.com                                              #
# @date: 31 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 01 Oct 2021 - Update some functions  (after line 114)        #      
#   (author: matilde.pato@gmail.com  )                                        # 
###############################################################################
#
# This file get abstracts, authors, year based on PubMed
#

### -- PMID
from metapub import PubMedFetcher
from Bio import Entrez
Entrez.email = <ENTER YOUR EMAIL HERE>
import unidecode
import time

from Utils.utils import valid_names, hasDashCharacter


# --------------------------------------------------------------------------- #

def get_pmid(pmcid):
    '''
    Return PubMed ID
    
    :param  pmcid:
    :return pmid:         
    '''
    try:
        article = PubMedFetcher().article_by_pmcid(pmcid)
        return article.pmid
    except:
        return []    

# --------------------------------------------------------------------------- #

def get_year_by_metapub(pmcid):
    '''
    Get PubMed year using metapub

    :param  pmcid:
    :return year         
    '''
    try:
        article = PubMedFetcher().article_by_pmcid(pmcid)
        return article.year
    except:
        return int() 

# --------------------------------------------------------------------------- #

def get_title_by_metapub(pmcid):
    '''
    Return PubMed ID
    
    :param  pmcid:
    :return pmid:         
    '''
    try:
        #article = fetch.article_by_pmid(pmid)
        article = PubMedFetcher().article_by_pmcid(pmcid)
        return article.title
    except:
        return []     

# --------------------------------------------------------------------------- #

def get_title_by_bio(pmid):
    ''' 
    Get PubMed year using Bio

    :param  pmid: PMID' article
    :return year
    '''
    try:
        handle = Entrez.esummary(db="pubmed", id=pmid, retmode="xml")
        record = Entrez.parse(handle)
        return record['Title']
    except:
        return [] 

# --------------------------------------------------------------------------- #

def get_abstract_by_bio(pmid):
    ''' 
    Get PubMed year using Bio

    :param  pmid: PMID' article
    :return year
    '''
    try:
        time.sleep(0.5)
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        record = Entrez.read(handle)
        handle.close()
        article = record['PubmedArticle'][0]['MedlineCitation']
        abstract = str()
                
        if 'Abstract' in article['Article'].keys(): # Some documents have no english abstract
            eng_content = article['Article']['Abstract']
        for element in eng_content['AbstractText']:
            abstract += element
        return abstract
    except:
        return [] 

# --------------------------------------------------------------------------- #

def get_year_by_bio(pmid):
    ''' 
    Get PubMed year using Bio

    :param  pmid: PMID' article
    :return year
    '''
    try:
        time.sleep(0.5)
        handle = Entrez.esummary(db="pubmed", id=pmid, retmode="xml")
        record = Entrez.parse(handle)
        return record['PubDate'].split()[0]
    except:
        return [] 

# --------------------------------------------------------------------------- #

def get_authors_by_bio(pmid):
    ''' 
    Get the authors list based on pmid's article

    :param  pmid: PMID' article
    :return authors list
    '''
    list_of_authors = []
    try:
        time.sleep(0.5)
        handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
        record = Entrez.read(handle)
        handle.close()
        article = record['PubmedArticle'][0]['MedlineCitation']
        # Get authors info: only consider articles with at least 1 author
        if 'AuthorList' in article['Article'].keys():
            for author in article['Article']['AuthorList']:   
                #Some authors are collective, e.g. 'ColectiveAuthor'          
                if 'ForeName' in author.keys() and 'LastName' in author.keys(): 
                    # remove all characters except alphabets from a string to unidecode
                    first = unidecode.unidecode( ''.join(m for m in author['ForeName'] if m.isalpha() or hasDashCharacter(author['ForeName'])) )
                    first = first.split(' ')[0]
                    #middle = unidecode.unidecode( ''.join(m for m in p['middle'] if m.isalpha()) )
                    last = unidecode.unidecode( ''.join(m for m in author['LastName'] if m.isalpha() or hasDashCharacter(author['LastName'])))

                    list_of_authors.append(last + ' '+ first)     
        
            if valid_names(list_of_authors):
                return valid_names(list_of_authors)
    finally:
        return list_of_authors


# --------------------------------------------------------------------------- #

def get_authors_by_metapub(pmcid):
    ''' 
    Get the authors list from PubMed based on pmcid's article

    :param  pmcid: PMCID' article
    :return list of authors 
    '''
    try:
        time.sleep(0.5)
        article = PubMedFetcher().article_by_pmcid(pmcid)
        if valid_names(article.authors):
            #print(article.authors)
            return valid_names(article.authors)
        return []
    except:
        return []     

""" # --------------------------------------------------------------------------- #

def get_authors_by_bio(pmid):
    ''' 
    Get PubMed year using Bio

    :param  pmid: PMID' article
    :return authors dictionary
    '''
    handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
    record = Entrez.read(handle)
    handle.close()
    article = record['PubmedArticle'][0]['MedlineCitation']
    authors = list()
    if 'AuthorList' in article['Article'].keys():# Get authors info: only consider articles with at least 1 author
            
        for author in article['Article']['AuthorList' ]:             
            if 'ForeName' in author.keys() and 'LastName' in author.keys(): #Some authors are collective, e.g. 'ColectiveAuthor'
                author_dict = {"first": author['ForeName'], "last": author['LastName']}            
                authors.append(author_dict) 
    return authors

# --------------------------------------------------------------------------- #

def get_authors_by_metapub(pmid):
    '''
    Get PubMed year using metapub

    :param  pmcid:
    :return year         
    '''
    fetch = PubMedFetcher()
    article = fetch.article_by_pmid(pmid)
    return article.authors    

# --------------------------------------------------------------------------- #

def check_authors_by_bio(pmid):
    ''' 

    :param  pmid: PMID' article
    :return year
    '''
    handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
    record = Entrez.read(handle)
    handle.close()
    article = record['PubmedArticle'][0]['MedlineCitation']
    # Get authors info: only consider articles with at least 1 author
    if 'AuthorList' in article['Article'].keys():
        return True
    return False


# --------------------------------------------------------------------------- #

def check_authors_by_metapub(pmcid):
    ''' 

    :param  pmid: PMID' article
    :return year
    '''
    fetch = PubMedFetcher()
    article = fetch.article_by_pmcid(pmcid)
    if article.authors:
        return True
    return False """    