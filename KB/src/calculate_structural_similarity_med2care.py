###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 23 Feb 2023                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
# @last update:                                                               #  
#   version 1.1: 24 Feb 2023 drop duplicate values from BD and get smiles of  #
#   chebi from a unique list of items                                         #      
#   (author: Matilde Pato)                                                    #
###############################################################################
#
# This module calculates the structural similarity between chebi' entities and 
# save the results in a mysql table. The input values is stored on mysql database
# previous saved in entities_sim_cord19_rs.similarity_chebi
#
# python3 calculate_structural_similarity_cord19.py   

# Metapub is a Python library that provides python

import pandas as pd
from datetime import datetime
from myconfiguration import MyConfiguration as cfg

from Utils.utils import save_metadata
from Utils.utils2database import check_database, save_to_mysql, get_values,\
    create_structuraltable, drop_duplicates

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

    """ def get_smile(str_dict):
        smile_dic={'smile1':[],'smile2':[]}
        try:
            c = ChEBI()
            if getattr(c.getCompleteEntity(str_dict['str1']),'smiles', None):
                sml1 = c.getCompleteEntity(str_dict['str1']).smiles 
                if getattr(c.getCompleteEntity(str_dict['str2']),'smiles', None):
                    sml2=c.getCompleteEntity(str_dict['str2']).smiles
                    smile_dic={'smile1':sml1,'smile2':sml2}
        except Exception as e:
            return smile_dic             
        return smile_dic """
    
    
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
            mol1 = molfromsmiles(smile['smile1'])
            mol2 = molfromsmiles(smile['smile2'])
            if mol1 is not None and mol2 is not None:
                #the Morgan fingerprint (similar to ECFP) is also useful:
                fp1 = rdMolDescriptors.GetMorganFingerprint(mol1,2)
                fp2 = rdMolDescriptors.GetMorganFingerprint(mol2,2)
                s = round(DataStructs.DiceSimilarity(fp1,fp2),7)
                return s
        except Exception as e:
            print(f'Morgan error. Error message {e}')
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
            print(f'Tanimoto error. Error message {e}')
            return None


    def get_smile(chebi_ids):
        ''' This function return a dataframe with smile values from chebi id
        '''
        import time
        smile_dic = pd.DataFrame(columns=['chebi', 'smile'])
        # Splitting list of items into multiple lists
        splitedSize = 499
        lst_chebi = [chebi_ids[i: i + splitedSize] for i in range(0, len(chebi_ids), splitedSize) ]
        
        for lst in lst_chebi:
            for i in range(len(lst)):
                try:
                    c = ChEBI()
                    if getattr(c.getCompleteEntity(lst.iloc[i]),'smiles', None):
                        sml = c.getCompleteEntity(lst.iloc[i]).smiles
                        pair = pd.DataFrame([{'chebi':lst.iloc[i],'smile':sml}])
                        smile_dic = pd.concat([smile_dic, pair],ignore_index=True) 
                        print(smile_dic.tail(10))  
                    time.sleep(0.5)    
                except Exception as e:
                    print(f'Error get smile: {lst.iloc[i]}')
                    continue             
        return smile_dic


    
    # remove duplicates if any
    drop_duplicates(tablename=table)
    # get entities from previous created table
    #
    cols_name = ["comp_1", "comp_2", "sim_tanimoto", "sim_morgan"]    
    chebi_df = get_values(table,sim='sim_resnik')

    chebi_df[cols_name[:2]] = chebi_df[cols_name[:2]].astype('int') 
    chebi_df[cols_name[0]]='CHEBI:'+chebi_df[cols_name[0]].astype(str).str.zfill(0)
    chebi_df[cols_name[1]]='CHEBI:'+chebi_df[cols_name[1]].astype(str).str.zfill(0)

    chebi_unique = pd.concat([chebi_df[cols_name[0]],chebi_df[cols_name[1]]],ignore_index=True).drop_duplicates()
    chebi_smile = get_smile(chebi_ids=chebi_unique)
    
    # create a second dataframe with molecule instead of chebi id to calculate the structural similarity
    chebi_df2 = pd.DataFrame(columns=cols_name[:2])
    # map values of Series according to an input mapping
    chebi_df2['comp_1'] = chebi_df[cols_name[0]].map(chebi_smile.set_index('chebi')['smile'])
    chebi_df2['comp_2'] = chebi_df[cols_name[1]].map(chebi_smile.set_index('chebi')['smile'])
    chebi_df2 = chebi_df2.dropna(subset=cols_name[:2])
    
    table_name='similarity_structural'
    onto = 'chebi'
    #create a new table with structural similarity values
    create_structuraltable('_'.join([table_name,onto]))  
    
    sim_df= pd.DataFrame(columns=cols_name)
    count = 0
    for i in range(chebi_df2.shape[0]):
        smile=dict({'smile1':chebi_df2['comp_1'].iloc[i],'smile2':chebi_df2['comp_2'].iloc[i]})
        pair = pd.DataFrame([{'comp_1':chebi_df2['comp_1'].iloc[i],'comp_2':chebi_df2['comp_2'].iloc[i], \
                        'sim_tanimoto':tanimoto_calc(smile), 'sim_morgan':morgan_calc(smile)}])
        # append values from orginal dataframe
        sim_df=pd.concat([sim_df, pair],ignore_index=True)
        print(sim_df.tail(10))
        count+=1

        if count>499:
            sim_df = sim_df.dropna(subset=cols_name[2:])
            sim_df['comp_1']=sim_df['comp_1'].map(chebi_smile.set_index('smile')['chebi']).str.extract('(\d+)').astype(int)
            sim_df['comp_2']=sim_df['comp_2'].map(chebi_smile.set_index('smile')['chebi']).str.extract('(\d+)').astype(int)
            # remove all NaN values as well as 0's
            sim_df = sim_df.loc[(sim_df[cols_name[2:]]!= 0).all(axis=1)]
            sim_df.reset_index()
            # creation of engine to MYSQL database to insert pandas DataFrame in the database
            save_to_mysql( sim_df.drop_duplicates(['comp_1','comp_2'], keep='first'), '_'.join([table_name,onto]), None )
            # reset all values
            print("***** SAVE IN MYSQL ********")
            sim_df= pd.DataFrame(columns=cols_name)
            count = 0

    if not sim_df.empty:
        sim_df['comp_1']=sim_df['comp_1'].map(chebi_smile.set_index('smile')['chebi']).str.extract('(\d+)').astype(int)
        sim_df['comp_2']=sim_df['comp_2'].map(chebi_smile.set_index('smile')['chebi']).str.extract('(\d+)').astype(int)
        # remove all NaN values as well as 0's
        sim_df = sim_df.dropna(subset=cols_name[2:])
        sim_df = sim_df.loc[(sim_df[cols_name[2:]]!= 0).all(axis=1)]
        sim_df.reset_index()
        # creation of engine to MYSQL database to insert pandas DataFrame in the database
        save_to_mysql( sim_df.drop_duplicates(['comp_1','comp_2'], keep='first'), '_'.join([table_name,onto]),None )
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