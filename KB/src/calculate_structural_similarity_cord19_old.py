###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 23 Feb 2023                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
# @last update:                                                               #  
#                                                                             #   
###############################################################################
#
# This module calculates the structural similarity between chebi' entities and 
# save the results in a mysql table. The input values is stored on mysql database
# previous saved in entities_sim_cord19_rs.similarity_chebi
#
# python3 calculate_structural_similarity_cord19.py   

# Metapub is a Python library that provides python

import os
import sys
import pandas as pd
from datetime import datetime
from myconfiguration import MyConfiguration as cfg

from Utils.utils import save_metadata
from Utils.utils2database import check_database, save_to_mysql, get_values,\
    create_structuraltable

from rdkit import Chem,DataStructs
from rdkit.Chem import rdMolDescriptors

from bioservices import ChEBI
#from indigo import *

pd.set_option('display.max_columns', None)
#pd.set_option("max_rows", None)
pd.options.display.max_rows = 999


# ---------------------------------------------------------------------------------------- #


def calculate_structural_sim(table):
    '''
    Calculate structural similarity, only for CHEBI ontology, and save the results in a
    novel table.
    :param table: name of the previous table. Assume that we have a table with other
    methods
    '''

    def get_smile(str_dict):
        c = ChEBI()
        smile_dic={'smile1':[],'smile2':[]}
        if getattr(c.getCompleteEntity(str_dict['str1']),'smiles', None):
            sml1 = c.getCompleteEntity(str_dict['str1']).smiles 
            if getattr(c.getCompleteEntity(str_dict['str2']),'smiles', None):
                sml2=c.getCompleteEntity(str_dict['str2']).smiles
                smile_dic={'smile1':sml1,'smile2':sml2}
        
        return smile_dic
    
    def molfromsmiles(smile):
        try:
            mol = Chem.MolFromSmiles(smile, sanitize=False)
            mol.UpdatePropertyCache(strict=False)
            Chem.SanitizeMol(mol,Chem.SanitizeFlags.SANITIZE_FINDRADICALS|Chem.SanitizeFlags.SANITIZE_KEKULIZE|Chem.SanitizeFlags.SANITIZE_SETAROMATICITY|Chem.SanitizeFlags.SANITIZE_SETCONJUGATION|Chem.SanitizeFlags.SANITIZE_SETHYBRIDIZATION|Chem.SanitizeFlags.SANITIZE_SYMMRINGS,catchErrors=True)
            return mol
        except Exception as e:
            return None
    

    def morgan_calc(smile):
        try:
            #the Morgan fingerprint (similar to ECFP) is also useful:
            mol1 = molfromsmiles(smile['smile1'])
            mol2 = molfromsmiles(smile['smile2'])
            if mol1 is not None and mol2 is not None: 
                fp1 = rdMolDescriptors.GetMorganFingerprint(mol1,2)
                fp2 = rdMolDescriptors.GetMorganFingerprint(mol2,2)
                s = round(DataStructs.DiceSimilarity(fp1,fp2),7)
                return s
        except Exception as e:
            #print(f'Morgan error. Error message {e}')
            return None
        return None


    def tanimoto_calc(smile):
        try:
            mol1 = molfromsmiles(smile['smile1'])
            mol2 = molfromsmiles(smile['smile2'])
            if mol1 is not None and mol2 is not None: 
                fp1 = Chem.RDKFingerprint(mol1) # AllChem.GetMorganFingerprintAsBitVect(mol1, 3, nBits=2048)
                fp2 = Chem.RDKFingerprint(mol2) # AllChem.GetMorganFingerprintAsBitVect(mol2, 3, nBits=2048)
                s = round(DataStructs.TanimotoSimilarity(fp1,fp2),7)
                return s
        except Exception as e:
            #print(f'Tanimoto error. Error message {e}')
            return None
        return None
      
    # get entities from previous created table
    # 
    chebi_df = get_values(table,sim='sim_resnik')
    chebi_df[["comp_1", "comp_2"]] = chebi_df[["comp_1", "comp_2"]].astype('int') 

    table_name='similarity_structural'
    onto = 'chebi'
    #create a new table with structural similarity values
    create_structuraltable('_'.join([table_name,onto]))
    cols_name = ["comp_1", "comp_2", "sim_tanimoto","sim_morgan"]
    sim_df= pd.DataFrame(columns=cols_name)

    count = 0
    for i in range(chebi_df.shape[0]):
        str1= onto.upper()+':'+str(chebi_df['comp_1'].values[i])
        str2= onto.upper()+':'+str(chebi_df['comp_2'].values[i])
        
        str_dict = {'str1':str1, 'str2':str2}
        smile = get_smile(str_dict)

        if smile:
            # #print(f'{i} {tanimoto_calc(res.smiles,res2.smiles)}')
            pair = pd.DataFrame([{'comp_1':int(chebi_df.at[i,'comp_1']),'comp_2':int(chebi_df.at[i,'comp_2']), \
                        'sim_tanimoto':tanimoto_calc(smile), 'sim_morgan':morgan_calc(smile)}])
            #print('count: ', count, '\n', pair)
            # append values from orginal dataframe
            sim_df=pd.concat([sim_df, pair],ignore_index=True)
            print(f'{i}: {sim_df.tail(10)}')
            count+=1

            if count>499:
                # remove all NaN values as well as 0's
                sim_df = sim_df.dropna(subset=cols_name[2:])
                sim_df = sim_df.loc[(sim_df[cols_name[2:]]!= 0).all(axis=1)]
                sim_df.reset_index()
                # creation of engine to MYSQL database to insert pandas DataFrame in the database
                save_to_mysql( sim_df.drop_duplicates(), '_'.join([table_name,onto]),None )
                # reset all values
                print("***** SAVE IN MYSQL ********")
                sim_df= pd.DataFrame(columns=cols_name)
                count = 0

    if not sim_df.empty:
        # remove all NaN values as well as 0's
        sim_df = sim_df.dropna(subset=cols_name[2:])
        sim_df = sim_df.loc[(sim_df[cols_name[2:]]!= 0).all(axis=1)]
        sim_df.reset_index()
        # creation of engine to MYSQL database to insert pandas DataFrame in the database
        save_to_mysql( sim_df.drop_duplicates(), '_'.join([table_name,onto]),None )
        print("***** END SAVE IN MYSQL ********")

# ---------------------------------------------------------------------------------------- #

def main():

    import time
    start_time = datetime.now()
    arg = cfg.getInstance()
   
    is_chebi = True
    # ---------------------------------------------------------------------------------------- #
    # connect to mysql table and create if not exists
    check_database()
    
    table_name = arg.tablename 
    if is_chebi:    
       calculate_structural_sim('_'.join([table_name,'chebi']))
    
    # ---------------------------------------------------------------------------------------- #
    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Calculation of structural similarity \n\
                Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                '
    save_metadata(arg.path_to_info, metadata) 
    print("FINISHED!")   
    exit() 

# ---------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()