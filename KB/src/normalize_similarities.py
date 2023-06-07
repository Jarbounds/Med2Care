###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email: matilde.pato@gmail.com                                              #
# @date: 12 June 2022                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
# @last update:                                                               #  
#   version 1.1:                                                              #      
#   (author:  )                                                 # 
#                                                                             #   
###############################################################################
#
# This module normalize the values of different similarities metrics obtained in
# calculate_similarity_cord19_recsys_ds.py
# The items should be defined by user

# python3 normalize_similarities.py
import math
import pandas as pd
import numpy as np
from sklearn import preprocessing
from datetime import datetime
from scipy import stats
from utils.myconfiguration import MyConfiguration as Config

from utils.utils2database import check_database, create_norm_table, get_column, save_to_mysql
from utils.utils import save_metadata

pd.set_option('display.max_columns', None)


def normalize(df, sim):
    tab = np.array(df[sim])
    norm_arr1 = preprocessing.normalize([tab], norm='l2')

    # Z-score normalization or Standardization
    # it is efficient only if your data is Gaussian-like distributed. It is also sensitive to the outliers
    norm_zscore = stats.zscore(tab)
    # Min-Max Scaling
    scaler = preprocessing.MinMaxScaler()
    norm_arr2 = scaler.fit_transform(pd.DataFrame(tab))

    # Tanh Estimator
    # Tanh estimators are considered to be more efficient and robust normalization technique. It is not sensitive 
    # to outliers, and it also converges faster than Z-score normalization. It yields values between -1 and 1
    # (Xi∈[−1,1]).
    norm_arr3 = [0.5 * np.tanh(tab - np.mean(tab)) / np.std(tab) * 0.01]

    # Sigmoid Normalization
    norm_arr4 = [1 / (1 + math.exp(-i)) for i in tab]

    pair_norm = pd.DataFrame({'l2': norm_arr1[0], 'zscore': norm_zscore, 'min-max': norm_arr2[:, 0],
                              'tanh': norm_arr3[0], 'log-sig': norm_arr4})
    # merge both dataframes
    return df.merge(pair_norm, left_index=True, right_index=True).reset_index(drop=True)


def database_norm(table, prefix, sim):
    result = get_column('_'.join([table, prefix]), column=sim)

    if len(result) != 0:
        table_norm = '_'.join(['norm', table, prefix, sim])
        create_norm_table(tablename=table_norm, sim=sim)
        result = pd.DataFrame(np.array(result), columns=['comp_1', 'comp_2', sim])
        return normalize(result, sim=sim), table_norm


def main():
    start_time = datetime.now()
    config = Config.get_instance()

    active_lexicons = config.item_prefix.replace(' ', '').split(',')

    # connect to mysql table
    database = config.database
    check_database(database)

    def get_table_name(similarity_name):
        return 'similarity_structural' if similarity_name in ["sim_tanimoto", "sim_morgan"] else config.tablename

    for onto in active_lexicons:
        sim_name = ["sim_resnik", "sim_lin", "sim_jc"]
        if onto.startswith('chebi'):
            sim_name.extend(["sim_tanimoto", "sim_morgan"])

        count = 0
        for s in sim_name:
            count += 1
            table_name = get_table_name(s)
            df, table_norm = database_norm(table=table_name, prefix=onto, sim=s)

            if not df.empty:
                # creation of engine to MYSQL database to insert pandas DataFrame in the database
                save_to_mysql(df=df.drop_duplicates(), table_name=table_norm, name_prefix='')

    print('SUCCESSFULLY NORMALIZED!')

    # save meta-information: date, time, database, dataset and ontology label in the txt file
    metadata = f'Date: {datetime.now()} \n \
                Duration: {datetime.now() - start_time} \n\
                Ontologies: {active_lexicons}\t No. entities: {df.shape[0]}\n\
                Results: {table_norm}\n\
                '
    save_metadata(config.path2info, metadata)
    print("FINISHED!")


if __name__ == '__main__':
    main()
