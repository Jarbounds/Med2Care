###############################################################################
#                                                                             #  
# @author: Matilde Pato (Adapted from André Lamurias)                         #  
# @email: matilde.pato@gmail.com                                              #
# @date: 31 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1:                                                              #      
#   (author: )                                                                #  
###############################################################################
#
# Import stop words vocabulary and tokenizer. Stop words are common words of a 
# given language (for example the words 'the', 'and', 'in'). A typical pre-p
# rocessing step is to tokenize the text and remove the stopwords. For that, 
# we are going to import NLTK's list of english stopwords and use the NLTK 
# tokenizer.
import copy
import os
import re

import merpy

## --- tokens
import nltk
nltk.download('stopwords')
nltk.download('punkt')
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize


# --------------------------------------------------------------------------- #

def update_mer(lexicon_name_list):
    """
    Update MER ontologies
    """
    print("Download latest obo files and process lexicons")
    merpy.download_mer()
    if len(lexicon_name_list) == 0:
        lexicon_name_list = ["doid", "go", "hpo", "chebi", "taxon", "cido"]
    for lexicon_name in lexicon_name_list:
        if lexicon_name == 'doid':
            merpy.download_lexicon("http://purl.obolibrary.org/obo/doid.owl", "do", ltype="owl")

            merpy.process_lexicon("do", ltype="owl")
            merpy.delete_obsolete("do")

        if lexicon_name == 'go':
            merpy.download_lexicon("http://purl.obolibrary.org/obo/go.owl", "go", ltype="owl")
            merpy.process_lexicon("go", ltype="owl")
            merpy.delete_obsolete("go")
        if lexicon_name == 'hp':
            merpy.download_lexicon("http://purl.obolibrary.org/obo/hp.owl", "hpo", ltype="owl")
            merpy.process_lexicon("hpo", ltype="owl")
            merpy.delete_obsolete("hpo")
            merpy.delete_entity("protein", "hpo")
            merpy.delete_entity_by_uri("http://purl.obolibrary.org/obo/PATO_0000070", "hpo")
        if lexicon_name == 'chebi':
            merpy.download_lexicon("http://purl.obolibrary.org/obo/chebi/chebi_lite.owl",
                                   # "ftp://ftp.ebi.ac.uk/pub/databases/chebi/ontology/chebi.owl",
                                   "chebi",
                                   ltype="owl",
                                   )
            merpy.process_lexicon("chebi", ltype="owl")
            merpy.delete_obsolete("chebi")
            merpy.delete_entity("protein", "chebi")
            merpy.delete_entity("polypeptide chain", "chebi")
            merpy.delete_entity("one", "chebi")
        if lexicon_name == 'taxon':
            merpy.download_lexicon("http://purl.obolibrary.org/obo/ncbitaxon.owl", "taxon", ltype="owl")
            merpy.process_lexicon("taxon", ltype="owl")
            merpy.delete_obsolete("taxon")
            merpy.delete_entity("data", "taxon")
        if lexicon_name == 'cido':
            merpy.download_lexicon("https://raw.githubusercontent.com/CIDO-ontology/cido/master/src/ontology/cido.owl",
                                   "cido",
                                   "owl",
                                   )
            merpy.process_lexicon("cido", "owl")
            merpy.delete_obsolete("cido")
            merpy.delete_entity("protein", "cido")


# --------------------------------------------------------------------------- #

def replace_problematic_chars(doc):
    with open('../data/replacers/chars.txt', 'r', encoding='utf-8') as file:
        invalid_chars = [char.rstrip() for char in file.readlines()]

    replaced_doc: str = copy.deepcopy(doc)
    for char in invalid_chars:
        replaced_doc = replaced_doc.replace(char, ' ')

    replaced_doc = re.sub(r'\s+', ' ', replaced_doc)

    return replaced_doc


def resolve_known_missing_terms(doc: str, lexicon: str) -> str:
    filename: str = ''
    if lexicon == 'chebi':
        filename = 'chebi.txt'
    elif lexicon in ['doid', 'do']:
        filename = 'doid.txt'
    elif lexicon == 'go':
        filename = 'go.txt'
    elif lexicon == 'hp':
        filename = 'hp.txt'

    if os.path.isfile(os.path.join('../data/replacers', filename)):
        doc_copy = copy.deepcopy(doc)
        with open(os.path.join('../data/replacers/', filename), 'r') as file:
            terms_list: list = [term.rstrip().split(';') for term in file.readlines()]
            terms: dict = dict(terms_list)

        for term in terms.items():
            # print(f'Replacing {term[0]} for {term[1]}')
            insensitive_regex = re.compile(re.escape(term[0]), re.IGNORECASE)
            doc_copy = insensitive_regex.sub(term[1], doc_copy)
            # print(f'doc_copy -> {doc_copy}')
        return doc_copy

    return doc


def items_in_blacklist(doc, lexicon):
    """
    Clear words from document that may distort the
    classification of the ontologies
    :param  doc: document
    :param  lexicon: prefix of the ontology
    :return doc
    """
    black_list = []

    # Removing stop words with NLTK and additional text
    all_stopwords = stopwords.words('english')
    filename = ''
    if lexicon == 'chebi':
        filename = 'chebi.txt'
    elif lexicon in ['doid', 'do']:
        filename = 'doid.txt'
    elif lexicon == 'go':
        filename = 'go.txt'
    elif lexicon == 'hp':
        filename = 'hp.txt'

    if os.path.isfile(os.path.join('../data/blacklists/', filename)):
        with open(os.path.join('../data/blacklists/', filename), 'r') as file:
            black_list = [content.rstrip() for content in file.readlines()]
        all_stopwords.extend(black_list)
    if os.path.isfile(os.path.join('../data/blacklists/', 'additional_words.txt')):
        with open(os.path.join('../data/blacklists/', 'additional_words.txt'), 'r') as file:
            black_list = [content.rstrip() for content in file.readlines()]
        all_stopwords.extend(black_list)

        # Tokenize and remove stop words
    doc_tokens = word_tokenize(doc.lower())
    doc_tokens_sw = [word for word in doc_tokens if word not in all_stopwords]

    return ' '.join(doc_tokens_sw)
