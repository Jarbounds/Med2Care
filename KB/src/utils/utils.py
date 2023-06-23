###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 31 Mar 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
# @last update:                                                               #  
#   version 1.1:                                                              #      
#   (author:   )                                                              # 
#                                                                             #   
#                                                                             #  
###############################################################################
import os
import pandas as pd
import numpy as np
from pathlib import Path


# --------------------------------------------------------------------------- #

def upload_dataset(csv_path, name_prefix):
    """

    Upload csv dataset which format is not "standard"
    :param csv_path: <user, item, rating, ... > csv file
    :param name_prefix: Prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    :return: pandas dataframe: <user, item, rating>
    """

    matrix = pd.read_csv(csv_path, sep=',', header=0)

    if matrix.dtypes['item'] == np.object:
        # filter rows for specific ontology
        matrix = matrix[matrix['item'].str.startswith(name_prefix)]

    return matrix


# --------------------------------------------------------------------------- #

def save_to_csv(df, path, header=False, index=False, sep=',', verbose=False):
    """
    Save data to csv file
    :param df: pandas Dataframe with columns <user, item, rating, ...>
    :param path: path to the csv file
    :return
    """
    if verbose:
        print("Saving df to path: {}".format(path))
        print("Columns in df are: {}".format(df.columns.tolist()))

    if not os.path.exists(os.path.dirname(path)):
        Path(os.path.dirname(path)).mkdir(parents=True, exist_ok=True)
    df.to_csv(path, header=header, index=index, sep=sep)


# --------------------------------------------------------------------------- #

def new_file(file):
    try:
        if not os.path.isfile(file):
            f = open(file, 'w')
    except OSError as error:
        print(error)

    # --------------------------------------------------------------------------- #


def save_metadata(file, line):
    '''
    This function will save all metadata about the process in txt file
    :param  filename: name of txt file
            line: all content
    :return none        
    '''

    if not os.path.exists(os.path.dirname(file)):
        Path(os.path.dirname(file)).mkdir(parents=True, exist_ok=True)

    new_file(file)
    with open(file, 'r+') as f:
        content = f.read()
        f.seek(0, 0)
        f.write(line.rstrip('\r\n') + '\n')
        f.write('------------------------------------------------------' + '\n' + content)
        f.close()
