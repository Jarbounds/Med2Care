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
#   version 1.4: 26 May 2022 - Add config.ini file                            #    
#   (author: matilde.pato@gmail.com  )                                        #    
#                                                                             #  
###############################################################################
#
# Find non valid articles after remove duplicate files, such as without authors
# (or, not valid), add abstract where non-found, and language is different from 
# predefined and write the paper_id to a txt files as a blacklist

# python3 cleaning_data.py 

import os
import configparser
from datetime import datetime, date

from utils.utils2json import read_json_file, get_revision_date, set_revision_date, write_json_file


def clean_date(data: dict) -> dict:
    """
    Cleans revision date field from JSON file

    :param  data: name of json file
    :return publish_date
    """

    formats: list[str] = [
        '%d/%m/%Y',
        '%d %B %Y',
        '%B %Y',
        '%m/%Y',
        '%d.%m.%Y'
    ]

    revision_date: str = get_revision_date(data)

    for date_format in formats:
        try:
            date_parsed: date = datetime.strptime(revision_date, date_format).date()
            return set_revision_date(data, str(date_parsed))
        except ValueError:
            print(f'date format "{date_format}" cannot be applied')

    print('NONE OF DATE FORMATS WERE APPLIED!!!')
    return data


def main():

    config = configparser.ConfigParser()
    config.read('../configurations/config.ini')

    input_dir = config['PATH']['extracted_medicines_dir']

    list_of_json_files = os.listdir(input_dir)

    for json_file in list_of_json_files:
        medicine_json: dict = read_json_file(input_dir, json_file)
        medicine_json = clean_date(medicine_json)
        write_json_file(input_dir, json_file, medicine_json)


if __name__ == '__main__':
    main()
