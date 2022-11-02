###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 20 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 27 mar 2022 save downloaded files into another disk          #      
#   (author: matilde.pato@gmail.com )                                         #  
#   version 1.2: 26 May 2022 - Add config.ini file                            #    
#   (author: matilde.pato@gmail.com  )                                        #  
#                                                                             #   
#                                                                             #  
###############################################################################
#
# Here we download and extract directly from url, based on date and tar.gz filename
#   Change path where you want to save files in the main() - line 146
#
# How to do:
# Before 2020-05-12:
# 1. python3 extract_from_url.py
# 2. python3 extract_from_url.py <date_iso_str> [<name_of_tar.gz_file2>] 
#    where <date_iso_str> = YYYY-MM-DD
#          <name_of_tar.gz_file2> = comm_use_subset.tar.gz 
#    e.g. python3 extract_from_url.py 2020-03-20 comm_use_subset.tar.gz
# After 2020-05-19:

# Since 2020-05-12 there are a significant breaking changes, and we found PDF and PMc folders
#   e.g. python3 extract_from_url.py 2020-05-19 [<document_parses.tar.gz>]

# With config.ini, just execute
#   e.g. python3 extract_from_url.py

import sys
import urllib.request
import requests
from requests.exceptions import HTTPError
import tarfile
import os
import shutil
from datetime import datetime
import configparser

# -------------------------------------------------------------------------------------- #

def extract_tar_gzip_directly( tarfilegz, src ):
    '''
    Extract all the contents of the tar.gz file to the current
    working directory
    :param  tarfilegz: name of the tar.gz file
            src: current working directory
    :return none
    '''
    os.chdir(src)
    if tarfile.is_tarfile(tarfilegz):
        archive = tarfile.open(tarfilegz)
        archive.extractall()
        archive.close()
    else:
        print('Some mistake! The file is not a tar')     

# -------------------------------------------------------------------------------------- #

def get_tar_from_url(url, file):
    '''
    Validate url 
    '''
    try:
        print( f'Validating url ... {file}' )
        response = requests.get(url)
        # If the response was successful, no Exception will be raised
        response.raise_for_status()

    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')  # Python 3.6
        sys.exit()
    except Exception as err:
        print(f'Other error occurred: {err}')  # Python 3.6 
        sys.exit()
    else:
        head, tail = os.path.split(url)
        print( f'Downloading {tail} ...' )
        urllib.request.urlretrieve(url, tail)  
 
        return tail   

# -------------------------------------------------------------------------------------- #

def get_default(file_name):
   
    if not file_name:
        print('Extract file!')
        file_name = 'comm_use_subset.tar.gz'
        date_iso_str = '2020-03-20'
    
    if after_20200519(date_iso_str):
        file_name = 'document_parses.tar.gz'  

    return date_iso_str, file_name

# -------------------------------------------------------------------------------------- #

def after_20200519(date):
    '''
    Check if file is recent, i.e. after 2020-05-19 (line 132)
    :param file: name of file
    :return boolean
    '''

    date_obj = datetime.strptime(date, '%Y-%m-%d')
    # # biggest changed in cord-19 format
    date_changed_format = datetime(2020, 5, 12)
    #datetime.strptime(date_str, '%Y-%m-%d')
    if date_obj > date_changed_format:
        return True
    return False    

# -------------------------------------------------------------------------------------- #

def main():

    config = configparser.ConfigParser()
    config.read('config.ini')

    date_iso_str = config['DS']['date']
    file_name = config['DS']['docname']

    date_iso_str, file_name = get_default(file_name)

    url = 'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/'

    # create a directory and save all files to there
    #new_folder(dir_to_save_data)
    
    os.chdir('/data/') 
    get_tar_from_url(url + date_iso_str + '/' + file_name, file_name)
    
    get_tar_from_url(url + date_iso_str + '/changelog', 'changelog')
    get_tar_from_url(url + date_iso_str + '/metadata.csv', 'metadata')    
    
    extract_tar_gzip_directly(file_name, '/data/')
    # remove tar file    
    os.remove(file_name)
    print('Finished!')

    
if __name__ == '__main__':

    main()

