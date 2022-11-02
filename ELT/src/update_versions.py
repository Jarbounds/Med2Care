###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 23 May 20212                                                         #
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
# Find duplicates documents between different versions downloaded
#
# python3 update_versions.py 

import os.path
import tempfile
import shutil
from tracemalloc import stop
import pandas as pd
import csv
import configparser

# --------------------------------------------------------------------------- #

def write2csv(list, file, date):
    '''
    Write a list of filenames into csv file
    :param  list: list of filenames
            file: filename where list will be store it
    :return none

    '''
    from datetime import datetime
    # storing current date and time
    # Iterating over all the data in the rows variable

    pair = pd.DataFrame([{'date':datetime.now(),'doc':val,'date_ds':date} for val in list ])
    pair.to_csv(file, index=False, sep=',')

# --------------------------------------------------------------------------- #

def main():

    config = configparser.ConfigParser()
    config.read('config.ini')

    pdf_dir = config['PATH']['pdf_dir']
    pmc_dir = config['PATH']['pmc_dir']

    ## read all filenames downloading (if done) before and stored in csv file
    list_old_files = config['PATH']['list_of_downloaded_file']

    old_files = []
    if os.path.isfile(list_old_files):
        with open(list_old_files, 'r', encoding='UTF8',newline='') as f:
            old_files = [line.strip().split(',')[1] for line in f]
            f.close() 
    ##
    ## save the list of all files to future interaction in csv
    ##

    ## read current files and store all the names in the csv file
    pdf_files, pmc_files = [], []
    pdf_files = [f for f in os.listdir(pdf_dir) if os.path.isdir(pdf_dir)]
    pmc_files = [f for f in os.listdir(pmc_dir) if os.path.isdir(pmc_dir)]
    
    # merge list without duplicates
    list_of_files = list(set(pdf_files + pmc_files))
    
    if not os.path.isfile(list_old_files):
        with open(list_old_files, 'w', encoding='UTF8',newline='') as f:
            write2csv(list=list_of_files, file=f, date=config['DS']['date'])
            f.close() 
    else:
        with open(list_old_files, 'a', encoding='UTF8',newline='') as f:
            write2csv(list=list_of_files, file=f, date=config['DS']['date'])
            f.close()     
    
    # ##
    # ## end of save filenames
    # ##
  
    duplicate_files = set()
    duplicate_files = [x for x in (list_of_files + old_files) if x in duplicate_files or (duplicate_files.add(x) or False)]
    
    ##remove all duplicate files in original path
    if len(duplicate_files)>0:
        temp_dir = tempfile.TemporaryDirectory()

        for ids in duplicate_files:
            if ids.startswith('PMC') :
                shutil.move(os.path.join(pmc_dir, ids), os.path.join(temp_dir, ids)) 
            elif os.path.isfile(os.path.join(pdf_dir, ids)):
                shutil.move(os.path.join(pdf_dir, ids), os.path.join(temp_dir, ids))  
   

# --------------------------------------------------------------------------- #

if __name__ == '__main__':
    
    main()
