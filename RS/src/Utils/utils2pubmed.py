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
Entrez.email = 'WRITE YOUR EMAIL ADDRESS'
import unidecode

from Utils.utils import valid_names, hasDashCharacter


# --------------------------------------------------------------------------- #

def get_pmid(pmcid):
    '''
    Return PubMed ID
    
    :param  pmcid:
    :return pmid:         
    '''
    article = PubMedFetcher().article_by_pmcid(pmcid)
    return article.pmid

# --------------------------------------------------------------------------- #

def get_year_by_metapub(pmcid):
    '''
    Get PubMed year using metapub

    :param  pmcid:
    :return year         
    '''
    article = PubMedFetcher().article_by_pmcid(pmcid)
    return article.year

# --------------------------------------------------------------------------- #

def get_title_by_metapub(pmcid):
    '''
    Return PubMed ID
    
    :param  pmcid:
    :return pmid:         
    '''
    #article = fetch.article_by_pmid(pmid)
    article = PubMedFetcher().article_by_pmcid(pmcid)
    return article.title

# --------------------------------------------------------------------------- #

def get_title_by_bio(pmid):
    ''' 
    Get PubMed title using Bio

    :param  pmid: PMID' article
    :return title
    '''
    handle = Entrez.esummary(db="pubmed", id=pmid, retmode="xml")
    record = Entrez.parse(handle)
    return record['Title']

# --------------------------------------------------------------------------- #

def get_abstract_by_bio(pmid):
    ''' 
    Get PubMed abstract using Bio

    :param  pmid: PMID' article
    :return abstract
    '''
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


# --------------------------------------------------------------------------- #

def get_year_by_bio(pmid):
    ''' 
    Get PubMed year using Bio

    :param  pmid: PMID' article
    :return year
    '''
    handle = Entrez.esummary(db="pubmed", id=pmid, retmode="xml")
    record = Entrez.parse(handle)
    return record['PubDate'].split()[0]

# --------------------------------------------------------------------------- #

def get_authors_by_bio(pmid):
    ''' 
    Get the authors list based on pmid's article

    :param  pmid: PMID' article
    :return authors list
    '''
    handle = Entrez.efetch(db="pubmed", id=pmid, retmode="xml")
    record = Entrez.read(handle)
    handle.close()
    article = record['PubmedArticle'][0]['MedlineCitation']
    # Get authors info: only consider articles with at least 1 author
    if 'AuthorList' in article['Article'].keys():
        list_of_authors = []
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
    return []


# --------------------------------------------------------------------------- #

def get_authors_by_metapub(pmcid):
    ''' 
    Get the authors list from PubMed based on pmcid's article

    :param  pmcid: PMCID' article
    :return list of authors 
    '''
    article = PubMedFetcher().article_by_pmcid(pmcid)
    if valid_names(article.authors):
        return valid_names(article.authors)
    return []
