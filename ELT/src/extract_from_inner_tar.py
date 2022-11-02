###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 20 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 26 May 2022 - Add config.ini file                            #    
#   (author: matilde.pato@gmail.com  )                                        #  
#                                                                             #   
#                                                                             #  
###############################################################################
#
# This is a special case where we will found and tar.gz inside another tar.gz, and
# we want to extract only the last one
#
# How to do:
# Before 2020-05-12:
# 1. python3 extract_from_inner_tar.py
#   in this case you must to change the url_variable in main function (after line 100)
# 2. python3 extract_from_inner_tar.py <name_of_tar.gz_file1> 
# 3. python3 extract_from_inner_tar.py <url_where_name_of_tar.gz_file_is>
# optional:
# 4. insert the name of the second tar.gz in command line, like:
#    python3 extract_from_inner_tar.py <name_of_tar.gz_file1> [<name_of_tar.gz_file2>] 
#     e.g. python3 extract_from_inner_tar.py cord-19_2020-03-20.tar.gz comm_use_subset.tar.gz
# After 2020-05-19:
# Since 2020-05-19 there are a significant breaking changes, and we found PDF and PMC folders
#   e.g. python3 extract_from_inner_tar.py cord-19_2020-05-19.tar.gz [<document_parses.tar.gz>]
#   if <document_parses.tar.gz> is not passed, the program evaluates the time period of the source

# With config.ini, just execute
#   e.g. python3 extract_from_inner_tar.py

import sys
import tarfile
import os
import requests
import shutil
import glob
from extract_from_url import *
from datetime import datetime

# -------------------------------------------------------------------------------------- #

def remote_extract_tar_gzip( tarfilegz1, tarfilegz2, path, dst ):
    '''
    Extract all the contents of the tar.gz file inside of another tar.gz
    :param  tarfilegz1: name of the first tar.gz file
            tarfilegz2: name of the inner tar.gz file
            path: path of the directory where tar.gz file is
            dst: new current working directory
    :return none
    '''
    if path:
        os.chdir(path)
        print("Current working directory: {0}".format(os.getcwd()))
    if tarfile.is_tarfile(tarfilegz1):
        
        archive = tarfile.open(tarfilegz1)
                
        path_file = ''
        flag = 0
        for tar in archive:
            
            if (tar.isdir()):
                path_file = tar.name
                flag = 1
                archive.extract(path_file+'/changelog')
                archive.extract(path_file+'/metadata.csv')
                print('Save metadata!')

            elif (tar.name == path_file+'/'+tarfilegz2):
                archive.extract(tar.name) 
                # extract inside of tar.gz file
                remote_extract_tar_gzip(tarfilegz2,'', path='./'+path_file, dst=dst)
            
            elif path:
                archive.extractall()
                archive.close() 
                return

            elif (tar.isfile() and flag==0):

                path_file = tar.name.split('/')[0]
                
                if tar.name.endswith('changelog'):
                
                    archive.extract(path_file+'/changelog')
                    os.replace(os.getcwd()+'/'+tar.name.split('/')[0]+'/changelog',os.getcwd()+'/'+dst+'/changelog')
                    os.remove(os.getcwd()+'/'+tar.name.split('/')[0])
                    print('Save changelog file!') 
                
                if tar.name.endswith('metadata.csv'):    
                    archive.extract(path_file+'/metadata.csv')
                    print('Save metadata!') 
                                                         
        archive.close()                   
        # activate this line if you want to remove tar file    
        os.remove(tarfilegz1)
    else:
        print('Some mistake! The file is not a tar.gz')      


# -------------------------------------------------------------------------------------- #

def change_path(src, dst):
    if not os.path.isdir(dst):
        os.makedirs(dst); 

    if os.path.isdir(src) and os.path.isdir(dst) :
    # Iterate over all the files in source directory
        for file in glob.glob(src + '/*'):
            # Move each file to destination Directory
            shutil.move(file, dst)

        
# -------------------------------------------------------------------------------------- #

def get_filename_without_extension(file_path):
    '''
    Grabs the basename from the path, splits the value on dots, and returns the first 
    one which is the initial part of the filename
    :param file_path: file name with extension
    :return file name without extension
    '''
    file_basename = os.path.basename(file_path)
    filename_without_extension = file_basename.split('.')[0]
    return filename_without_extension

# -------------------------------------------------------------------------------------- #

def exists_file_current_path(file):
    '''
    Check if file is in system
    :param file: name of file to be extracted
    :return boolean
    '''
    listFiles = os.listdir(os.getcwd())
    for file in listFiles:
        if file.endswith('tar.gz'):
            return True
    return False        

# -------------------------------------------------------------------------------------- #

def after_20200519(file):
    '''
    Check if file is recent, i.e. after 2020-05-19 (line 132)
    :param file: name of file
    :return boolean
    '''
    date_str = get_filename_without_extension(file).split('_',1)[1]
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')

    # # biggest changed in cord-19 format
    date_changed_format = datetime(2020, 5, 12)    
    if date_obj > date_changed_format:
        return True
    return False  

# -------------------------------------------------------------------------------------- #

def get_tar_name(file_name, tar_file1, url):
    
    if not tar_file1:
        tar_file1 = 'cord-19_2020-05-19.tar.gz'   

    if not exists_file_current_path(tar_file1): 
        if file_name:
            tar_file1 = get_tar_from_url(url + tar_file1, file_name)  
        elif tar_file1.endswith('tar.gz'):            
            if exists_file_current_path(tar_file1):
                tar_file1 = tar_file1 
            else:    
                tar_file1 = get_tar_from_url(url + tar_file1, tar_file1)        
        elif requests.get(tar_file1):           
            tar_file1 = get_tar_from_url(tar_file1, '')
    return tar_file1
    
# -------------------------------------------------------------------------------------- #

def get_default(file_name, date):
    
    if after_20200519(date):
        file_name = 'document_parses.tar.gz'  
    else:
        file_name = 'comm_use_subset.tar.gz'

    return file_name

# -------------------------------------------------------------------------------------- #

def main():

    config = configparser.ConfigParser()
    config.read('config.ini')

    file_name = config['DS']['docname']
    tar_file1 = config['DS']['tar_document']

    url = 'https://ai2-semanticscholar-cord-19.s3-us-west-2.amazonaws.com/historical_releases/'    

    
    tar_file1 = get_tar_name(file_name, tar_file1, url)
    
    os.chdir('/data/')
    date_iso_str = get_filename_without_extension(tar_file1).split('_',1)[1]

    file_name = get_default(file_name, date_iso_str)
    
    remote_extract_tar_gzip(tarfilegz1=tar_file1, tarfilegz2=file_name, path='', dst = date_iso_str)
        
    #change_path(os.path.dirname(os.path.realpath(__file__))+'/'+date_iso_str, \
    #    os.path.dirname(os.getcwd())+'/'+dir_to_save_data)
    shutil.rmtree(os.path.dirname(os.path.realpath(__file__))+'/'+date_iso_str)

    print('Finished!')


if __name__ == '__main__':
    
    main()
