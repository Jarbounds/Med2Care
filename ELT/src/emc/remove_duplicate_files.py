###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 09 Apr 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 26 May 2022 - Add configurations.ini file                            #
#   (author: matilde.pato@gmail.com  )                                        #  
#                                                                             #   
#                                                                             #  
###############################################################################
#
# Find duplicates articles in pmc and non-pmc folders, and copy/move uniques to 
# another folder
#
# python3 remove_duplicate_files.py [<option>]
#  where option = 'copy' or 'move' files
#  by default = 'copy'
# version 1.1
# python3 remove_duplicate_files.py

import os
import configparser

import pandas as pd
from pandas import DataFrame
from datetime import date, datetime, timedelta
from utils.utils import transfer_file, save_metadata
from utils.utils2json import read_json_file, get_medicine_id, get_revision_date, get_emc_id


# --------------------------------------------------------------------------- #

def get_ids(src) -> dict[str, str]:
    """
    Get dictionary for filename and medicine id
    :param  src: path where file is
    :return list containing the filenames and list containing the medicine ids
    """

    ids: dict[str, str] = {}

    for file in os.listdir(src):
        try:
            medicine_json: dict = read_json_file(src, file)
            medicine_id: str = get_medicine_id(medicine_json)
            emc_id: str = get_emc_id(medicine_json)
            ids[emc_id] = medicine_id
        except Exception as e:
            print(f'file {file} not found, printing exception\n{e}')

    return ids


def check_overlapped(overlapped: DataFrame, extracted_dir: str, processed_dir: str) -> tuple[int, DataFrame]:
    new_ids: list = []
    count: int = 0
    for identifier in overlapped.id.values:
        extracted_medicine_doc: dict = read_json_file(extracted_dir, identifier)
        processed_medicine_doc: dict = read_json_file(processed_dir, identifier)

        revision_date_extracted: str = get_revision_date(extracted_medicine_doc)
        revision_date_processed: str = get_revision_date(processed_medicine_doc)

        date_extracted: date = datetime.strptime(revision_date_extracted, '%Y-%m-%d').date()
        date_processed: date = datetime.strptime(revision_date_processed, '%Y-%m-%d').date()

        if date_extracted > date_processed:
            new_ids.append(identifier)
        elif date_extracted == date_processed:
            count += 1

    return count, DataFrame(new_ids, columns=['id'])


def verify_duplicate_files(extracted_dir: str, processed_dir: str) -> tuple[int, list]:
    """
    Find duplicate files between the current extracted medicines and the previous ones

    :param extracted_dir: directory of the recently extracted medicines
    :param processed_dir: directory for the previously processed medicines
    :return list of documents to keep no. of duplicates
    """

    extracted_ids: dict[str, str] = get_ids(extracted_dir)
    processed_ids: dict[str, str] = get_ids(processed_dir)

    df_extracted: DataFrame = DataFrame(
        extracted_ids.items(),
        columns=['emc_id', 'id']
    )
    df_processed: DataFrame = DataFrame(
        processed_ids.items(),
        columns=['emc_id', 'id']
    )

    overlapped: DataFrame = df_extracted[df_extracted.emc_id.isin(df_processed.emc_id)]
    number_duplicates, overlapped_to_keep = check_overlapped(overlapped, extracted_dir, processed_dir)

    new_medicines: DataFrame = df_extracted[~df_extracted.id.isin(df_processed.id)]

    to_return: DataFrame = pd.concat([overlapped_to_keep, new_medicines])

    return number_duplicates, to_return['id'].values.tolist()


def main():
    from datetime import datetime

    start_time = datetime.now()
    
    config = configparser.ConfigParser()
    config.read('../configurations/configurations.ini')

    staged_data_dir: str = config['PATH']['staged_data_dir']

    cleaned_medicines_dir: str = config['PATH']['cleaned_medicines_dir']
    processed_medicines_dir: str = config['PATH']['processed_medicines_dir']

    os.makedirs(processed_medicines_dir, exist_ok=True)

    total_files: int = len(os.listdir(cleaned_medicines_dir))

    print(f'Number of medicine files to check: {total_files}')

    # Find duplicates files and return a list of overlapped ids to keep and new ids to add.
    # The number of duplicates will be count
    count_duplicate, overlapped_ids_to_keep = verify_duplicate_files(
        extracted_dir=cleaned_medicines_dir,
        processed_dir=processed_medicines_dir
    )

    files_to_keep: list[str] = [f'{id_v}.json' for id_v in overlapped_ids_to_keep]

    transfer_file(
        lst_files=files_to_keep,
        src=cleaned_medicines_dir,
        dst=processed_medicines_dir,
        flag=config['TRANSFER']['option']
    )

    transfer_file(
        lst_files=files_to_keep,
        src=cleaned_medicines_dir,
        dst=staged_data_dir,
        flag=config['TRANSFER']['option']
    )

    duration: timedelta = datetime.now() - start_time

    metadata = \
        f'Date: {datetime.now()}\n'\
        f'Duration: {duration}\n'\
        f'Initial data: {total_files}\n'\
        f'Number of medicine docs transferred: {len(files_to_keep)}\n'\
        f'No. of duplicate-articles: {count_duplicate}\n'

    save_metadata(filename=config['PATH']['path_to_info'], line=metadata)

    print(f'Duration: {duration}')


if __name__ == '__main__':
    main()
