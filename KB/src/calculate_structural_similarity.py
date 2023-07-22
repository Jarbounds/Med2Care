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
#   version 1.2: 1 Mar 2023 fix problems caused by map function, since the    #
#   the items doesn't exist in SMILE list: changing to merge, fix problems    #
#   caused by NonType and 'float' object is not subscriptable since we cannot #
#   calculate Tanimoto and Morgan similarities: add a new user defined class  #      
#   (author: Matilde Pato)                                                    #                                                                             #   
###############################################################################
#
# This module calculates the structural similarity between chebi' entities and 
# save the results in a mysql table. The input values is stored on mysql database
# previous saved in entities_sim_cord19_rs.similarity_chebi
#
# python3 calculate_structural_similarity.py

# Metapub is a Python library that provides python

import time
import pandas as pd
from datetime import datetime

from utils.utils import save_metadata
from utils.utils2database import check_database, save_to_mysql, get_db_values, \
    create_structural_table, drop_duplicates, get_minmax
from utils.myconfiguration import MyConfiguration as Config
from rdkit import Chem, DataStructs
from rdkit.Chem import rdMolDescriptors

from bioservices import ChEBI
from multiprocessing.pool import ThreadPool, Pool

# from indigo import *

pd.set_option('display.max_columns', None)
# pd.set_option("max_rows", None)
pd.options.display.max_rows = 999


# fix TypeError: 'float' object is not subscriptable
class MyFloat:
    def __init__(self, f):
        self.f = f

    def __getitem__(self, index):
        return self.f


# ---------------------------------------------------------------------------------------- #


def calculate_structural_sim(simtable, str_simtable, minid=None, limit=None):
    """
    Calculate structural similarity, only for CHEBI ontology, and save the results in a
    novel table.
    :param table: name of the previous table. Assume that we have a table with other
    methods
    """

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
        return smile_dic 
        
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
                print(f'Tanimoto and Morgan error. Error message {e}')
            return None
        """

    def molfromsmiles(smile):
        try:
            mol = Chem.MolFromSmiles(smile, sanitize=False)
            mol.UpdatePropertyCache(strict=False)
            Chem.SanitizeMol(mol,
                             Chem.SanitizeFlags.SANITIZE_FINDRADICALS | Chem.SanitizeFlags.SANITIZE_KEKULIZE | Chem.SanitizeFlags.SANITIZE_SETAROMATICITY | Chem.SanitizeFlags.SANITIZE_SETCONJUGATION | Chem.SanitizeFlags.SANITIZE_SETHYBRIDIZATION | Chem.SanitizeFlags.SANITIZE_SYMMRINGS,
                             catchErrors=True)
            return mol
        except Exception as e:
            print(f'Molecule error. Error message {e}')
        return None

    def str_simil(smile):
        sim_dict = dict({'tanimoto': 0.0, 'morgan': 0.0})
        try:
            mol1 = molfromsmiles(smile['smile1'])
            mol2 = molfromsmiles(smile['smile2'])
            if mol1 is not None and mol2 is not None:
                fp1 = Chem.RDKFingerprint(mol1)  # AllChem.GetMorganFingerprintAsBitVect(mol1, 3, nBits=2048)
                fp2 = Chem.RDKFingerprint(mol2)  # AllChem.GetMorganFingerprintAsBitVect(mol2, 3, nBits=2048)
                s = round(DataStructs.TanimotoSimilarity(fp1, fp2), 7)
                my_float = MyFloat(s)
                sim_dict['tanimoto'] = my_float[0]

                # the Morgan fingerprint (similar to ECFP) is also useful:
                fp1 = rdMolDescriptors.GetMorganFingerprint(mol1, 2)
                fp2 = rdMolDescriptors.GetMorganFingerprint(mol2, 2)
                s = round(DataStructs.DiceSimilarity(fp1, fp2), 7)
                my_float = MyFloat(s)
                sim_dict['morgan'] = my_float[0]
                return sim_dict
        except Exception as e:
            print(f'Tanimoto and Morgan error. Error message {e}')
        return sim_dict

    def get_smile(chebi_ids):
        ''' This function return a dataframe with smile values from chebi id
        '''
        smile_dic = pd.DataFrame(columns=['chebi', 'smile'])
        # Splitting list of items into multiple lists
        # splitedSize = 499
        # lst_chebi = [chebi_ids[i: i + splitedSize] for i in range(0, len(chebi_ids), splitedSize) ]

        # for lst in lst_chebi:
        for i in range(len(chebi_ids)):
            try:
                c = ChEBI()
                if getattr(c.getCompleteEntity(chebi_ids.iloc[i]), 'smiles', None):
                    sml = c.getCompleteEntity(chebi_ids.iloc[i]).smiles
                    pair = pd.DataFrame([{'chebi': chebi_ids.iloc[i], 'smile': sml}])
                    smile_dic = pd.concat([smile_dic, pair], ignore_index=True)
            except Exception as e:
                print(f'Error get smile: {chebi_ids.iloc[i]}')
                continue
        return smile_dic

    cols_name = ["comp_1", "comp_2", "sim_tanimoto", "sim_morgan"]

    # get entities from previous created table    

    chebi_df = get_db_values(simtable, minid, limit)

    chebi_df[cols_name[:2]] = chebi_df[cols_name[:2]].astype('int')
    chebi_df[cols_name[0]] = 'CHEBI:' + chebi_df[cols_name[0]].astype(str).str.zfill(0)
    chebi_df[cols_name[1]] = 'CHEBI:' + chebi_df[cols_name[1]].astype(str).str.zfill(0)
    # chebi_df.to_csv(f"chebi_table.csv",mode='a',encoding='utf-8',index=True)
    # chebi_df=pd.DataFrame(columns=['comp_1', 'comp_2'])
    # chebi_df = pd.read_csv("chebi_table.csv")

    chebi_unique = pd.concat([chebi_df[cols_name[0]], chebi_df[cols_name[1]]], ignore_index=True).drop_duplicates()
    # Splitting list of items into multiple lists
    chunk_size = 1000
    lst_chebi = [chebi_unique[i: i + chunk_size] for i in range(0, len(chebi_unique), chunk_size)]

    for lst in lst_chebi:
        chebi_smile = pd.DataFrame()
        chebi_smile = get_smile(chebi_ids=lst)
        print(f'Processing chebi ids: {lst}')
        """ #---------
        #chebi_smile.to_csv("chebi_table1.csv",mode='a',encoding='utf-8',index=False) 
        
        chebi_smile = pd.read_csv("chebi_table1.csv",index_col=False)
        chebi_smile = chebi_smile[["chebi","smile"]]
         """
        # drop rows where corresponding smile doesn't exist -- refresh dataframe
        # note: include parenthesis around each individual condition when filtering a pandas DataFrame by multiple conditions
        chebi_df = chebi_df[(chebi_df[cols_name[0]].isin(chebi_smile.chebi.values.tolist())) & (
            chebi_df[cols_name[1]].isin(chebi_smile.chebi.values.tolist()))]
        chebi_df.reset_index(inplace=True, drop=True)

        # create a second dataframe with molecule instead of chebi id to calculate the structural similarity
        # chebi_df2 = pd.DataFrame(columns=cols_name[:2])
        # map values of Series according to an input mapping
        # chebi_df2[cols_name[0]] = chebi_df[cols_name[0]].map(chebi_smile.set_index('chebi')['smile'])
        # chebi_df2[cols_name[1]] = chebi_df[cols_name[1]].map(chebi_smile.set_index('chebi')['smile'])

        chebi_df2 = pd.merge(chebi_df, chebi_smile, left_on=['comp_1'], right_on=['chebi'], how="left")
        # drop extra column
        chebi_df2.drop("chebi", axis=1, inplace=True)
        chebi_df2 = pd.merge(chebi_df2, chebi_smile, left_on=['comp_2'], right_on=['chebi'], how="left")
        # drop extra column
        chebi_df2.drop("chebi", axis=1, inplace=True)
        chebi_df2 = chebi_df2.rename(columns={"smile_x": "smile1", "smile_y": "smile2"})
        chebi_df2 = chebi_df2[["comp_1", "comp_2", "smile1", "smile2"]].drop_duplicates(
            ['comp_1', 'comp_2']).reset_index(drop=True)
        # chebi_df2.to_csv("chebi_table2.csv",encoding='utf-8',index=False)

        # remove rows where entities are equal (avoid sim = 1)
        chebi_df2 = chebi_df2[chebi_df2[cols_name[0]] != chebi_df2[cols_name[1]]]

        sim_df = pd.DataFrame(columns=cols_name)
        count = 0
        for i in range(chebi_df2.shape[0]):

            smile = dict({'smile1': chebi_df2['smile1'].iloc[i], 'smile2': chebi_df2['smile2'].iloc[i]})
            str_sim = str_simil(smile)
            pair = pd.DataFrame([{'comp_1': chebi_df2[cols_name[0]].iloc[i], 'comp_2': chebi_df2[cols_name[1]].iloc[i], \
                                  'sim_tanimoto': str_sim['tanimoto'], 'sim_morgan': str_sim['morgan']}])
            # append values from orginal dataframe
            if pair[:2] is not None:
                sim_df = pd.concat([sim_df, pair]).reset_index(drop=True)
            count += 1

            if count > 499:
                sim_df[cols_name[0]] = sim_df[cols_name[0]].str.extract('(\d+)').astype(int)
                sim_df[cols_name[1]] = sim_df[cols_name[1]].str.extract('(\d+)').astype(int)
                # map doesn't work well
                # sim_df[cols_name[0]]=sim_df[cols_name[0]].map(chebi_smile.set_index('smile')['chebi']).str.extract('(\d+)').astype(int)
                # sim_df[cols_name[1]]=sim_df[cols_name[1]].map(chebi_smile.set_index('smile')['chebi']).str.extract('(\d+)').astype(int)

                # remove all NaN values as well as 0's
                sim_df = sim_df.dropna(subset=cols_name[2:])
                sim_df = sim_df.loc[(sim_df[cols_name[2:]] != 0).all(axis=1)]
                sim_df.reset_index(inplace=True, drop=True)

                # creation of engine to MYSQL database to insert pandas DataFrame in the database
                save_to_mysql(sim_df.drop_duplicates(cols_name[:2], keep='first'), str_simtable, None)
                # reset all values
                print("***** SAVE IN MYSQL ********")
                sim_df = pd.DataFrame(columns=cols_name)
                count = 0
                time.sleep(0.5)

        if not sim_df.empty:
            sim_df[cols_name[0]] = sim_df[cols_name[0]].str.extract('(\d+)').astype(int)
            sim_df[cols_name[1]] = sim_df[cols_name[1]].str.extract('(\d+)').astype(int)

            # remove all NaN values as well as 0's
            sim_df = sim_df.dropna(subset=cols_name[2:])
            sim_df = sim_df.loc[(sim_df[cols_name[2:]] != 0).all(axis=1)]
            sim_df.reset_index(inplace=True, drop=True)

            # creation of engine to MYSQL database to insert pandas DataFrame in the database
            save_to_mysql(sim_df.drop_duplicates(cols_name[:2], keep='first'), str_simtable, None)
            print("***** SAVE IN MYSQL ********")


def main():
    start_time = datetime.now()
    config = Config.get_instance()

    # connect to mysql table and create if not exists
    database = config.database
    check_database(database)

    active_lexicon = config.item_prefix
    # split if there is a list of entities
    active_lexicon = active_lexicon.replace(' ', '').split(',')

    onto = 'chebi'
    if onto not in active_lexicon:
        print("The is no CHEBI items")
        exit()
    old_table = '_'.join([config.tablename, onto])
    print(old_table)

    onto = 'chebi'
    new_table = '_'.join(['similarity_structural', onto])

    # create a new table with structural similarity values
    create_structural_table(new_table)
    # parameter for using in sql query, where we define the value of the primary key (id) mininum, and
    # the no. of rows
    limit = 1000
    min_id, max_id = get_minmax(table_name=old_table)['min'], get_minmax(table_name=old_table)['max']

    if min_id:
        with Pool() as pool:
            params = []
            while min_id <= max_id:
                params.append(
                    (old_table, new_table, min_id, limit)
                )
                min_id += limit
            pool.starmap(calculate_structural_sim, params)
    else:
        calculate_structural_sim(old_table, new_table, min_id, limit)
    # remove duplicates if any
    drop_duplicates(table_name=new_table)
    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Calculation of structural similarity \n\
                Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                '
    save_metadata(config.path2info, metadata)
    print("FINISHED!")


if __name__ == '__main__':
    main()
