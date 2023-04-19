###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 03 May 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 28 May 2021 - change textblob to googletrans                 #      
#   (author: matilde.pato@gmail.com  )                                        # 
#   version 1.2: 01 Oct 2021 - Remove googletrans and use langdetect          #  
#   check valid author names with spacy                                       #      
#   (author: matilde.pato@gmail.com  )                                        #    
#   version 1.3: 27 Mar 2022 - Check date if exist, put blacklist in dict and #
#   save at the end                                                           #    
#   (author: matilde.pato@gmail.com  )                                        #  
#   version 1.4: 26 May 2022 - Add configurations.ini file                            #
#   (author: matilde.pato@gmail.com  )                                        #    
#                                                                             #  
###############################################################################
#
# Find non valid articles after remove duplicate files, such as without authors
# (or, not valid), add abstract where non-found, and language is different from 
# predefined and write the paper_id to a txt files as a blacklist

# python3 cleaning_data.py

import os
import re
import copy
import configparser
from dateutil import parser

from utils.utils2json import \
    read_json_file, get_revision_date, set_revision_date, write_json_file, get_member_recursive, set_member_recursive


def normalize_date(data: dict) -> dict:
    """
    Cleans revision date field from JSON file

    :param  data: name of json file
    :return updated data dict with parsed revision date
    """

    revision_date: str = get_revision_date(data)

    try:
        revision_date = all_normalizations(revision_date)
        # Removes unnecessary bloat
        revision_date = ' '.join(revision_date.split(' ')[:3])
        # Try to auto parse date from string
        revision_date = str(parser.parse(revision_date).date())
        return set_revision_date(data, revision_date)
    except Exception as date_error:
        print('Cannot auto parse date field')
        print('Trying particular parse')
        try:
            revision_date = ' '.join(revision_date.split(' ')[:2])
            revision_date = str(parser.parse(revision_date).date())
            return set_revision_date(data, revision_date)
        except Exception as date_error_part:
            print('ERROR: There is a problem with revision date field')
            print(date_error)
            print(date_error_part)


def all_normalizations(member: str) -> str:
    member = re.sub(r'[^\w\s]', ' ', member)
    member = re.sub(r'\n+', ' ', member)
    member = re.sub(r'\t+', ' ', member)
    member = re.sub(r'\r+', ' ', member)
    member = re.sub(r'\s+', ' ', member)
    member = member.strip()
    return member


def normalize_general(data: dict) -> dict:
    normalized_data: dict = copy.deepcopy(data)

    name: str = get_member_recursive(normalized_data, 'name')
    composition: str = get_member_recursive(normalized_data, 'composition')
    therapeutic_indications: str = get_member_recursive(normalized_data, 'therapeutic_indications')
    disease: str = get_member_recursive(normalized_data, 'disease')

    name = all_normalizations(name)
    composition = all_normalizations(composition)
    therapeutic_indications = all_normalizations(therapeutic_indications)
    disease = all_normalizations(disease)

    set_member_recursive(normalized_data, 'name', name)
    set_member_recursive(normalized_data, 'composition', composition)
    set_member_recursive(normalized_data, 'therapeutic_indications', therapeutic_indications)
    set_member_recursive(normalized_data, 'disease', disease)

    return normalized_data


def main():

    config = configparser.ConfigParser()
    config.read('../configurations/configurations.ini')

    input_dir = config['PATH']['extracted_medicines_dir']
    output_dir = config['PATH']['cleaned_medicines_dir']

    list_of_json_files = os.listdir(input_dir)

    for json_file in list_of_json_files:
        medicine_json: dict = read_json_file(input_dir, json_file)
        medicine_json = normalize_general(medicine_json)
        medicine_json = normalize_date(medicine_json)
        write_json_file(output_dir, json_file, medicine_json)


if __name__ == '__main__':
    main()
