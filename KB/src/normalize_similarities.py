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
# This module normalize the values of diferent similarities metrics obtained in
# calculate_similarity_cord19_recsys_ds.py
# The items should be defined by user

# python3 normalize_similarities.py   


import math
import pandas as pd
import numpy as np
from sklearn import preprocessing
from datetime import datetime
from scipy import stats
from myconfiguration import MyConfiguration as cfg

from Utils.utils2database import check_database, create_norm_table, get_column, save_to_mysql

pd.set_option('display.max_columns', None)
pd.set_option("max_rows", None)


# tab = np.array([0.271997,0.469086,0.0718948,0.527258, 1.80328, 2.13386,0.0718948,0.527258,0.527258, 2.13386,0.527258, 
# 2.13386,0.527258,0.527258, 2.13386,0.425774,0.0718948,0.527258,0.527258,0.527258,0.527258,0.271997,0.527258,
# 0.527258,0.527258,0.469086,0.271997,0.527258,0.527258,0.527258,       0,       0,       0,       0,       0, 
#       0, 4.61904,       0,       0,       0,       0,       0,       0,       0,       0,       0,       0,
#       0.358334, 5.00451, 4.36758,0.425774, 1.99209, 1.12449,0.425774, 1.99209, 1.99209, 1.99209, 1.99209,
#       0.425774, 1.99209, 4.36758,0.358334, 1.99209,      -0,0.0432674,0.0432674,0.425774,0.425774,0.0432674,
#       0.0432674,0.425774,0.425774,0.425774,0.425774,0.425774,0.425774,0.425774,0.425774,0.425774,0.425774,
#       0.0432674,0.425774,0.0432674,0.0432674,0.425774,0.425774,0.425774,0.0432674,0.425774,0.425774,0.425774,
#       0.425774,0.369853,0.425774,0.0432674,0.425774,0.425774,0.425774,0.425774,0.425774,0.425774,      -0, 
#       2.58626, 1.61402, 1.61402, 1.12449, 1.54952, 1.12449, 1.12449, 1.61402, 1.61402,0.899524, 3.54596, 
#       1.27744,0.899524, 1.71024, 1.71024, 1.71024, 5.11501, 1.27744, 1.27744,0.527258, 1.71024, 1.27744,
#       0.899524,0.358334,0.358334, 1.71024, 2.00323, 1.71024, 1.71024,0.358334,0.271997, 1.71024, 2.00323, 
#       1.27744, 1.27744, 1.27744,0.425774, 1.71024, 1.71024, 2.55926,0.358334,0.358334,0.358334,0.358334,
#       0.358334,0.358334,0.358334,0.358334,0.358334,0.358334,0.0718948,0.358334,0.358334,0.358334,0.358334,
#       0.358334,0.358334,0.358334,0.358334,0.358334,0.358334,0.358334,0.358334,0.358334,0.358334,0.358334,
#       0.358334,0.358334,0.358334,0.358334])

def normalize(df,sim):

    tab = np.array(df[sim])
    norm_arr1 = preprocessing.normalize([tab], norm='l2')

    ## Z-score normalization or Standardization
    # it is efficient only if your data is Gaussian-like distributed. It is also sensitive to the outliers
    norm_zscore = stats.zscore(tab)
    ## Min-Max Scaling
    scaler = preprocessing.MinMaxScaler()
    norm_arr2 = scaler.fit_transform(pd.DataFrame(tab))

    ## (Modified) Tanh Estimator
    # Tanh estimators are considered to be more efficient and robust normalization technique. It is not sensitive 
    # to outliers and it also converges faster than Z-score normalization. It yields values between -1 and 1 
    # (Xi∈[−1,1]).
    norm_arr3 = [0.5 * np.tanh(tab - np.mean(tab))/np.std(tab)*0.01]

    ## Sigmoid Normalization
    norm_arr4 = [ 1/(1+math.exp(-i)) for i in tab]

    pair_norm = pd.DataFrame({'l2': norm_arr1[0], 'zscore': norm_zscore, 'min-max': norm_arr2[:,0],
        'tanh': norm_arr3[0], 'log-sig': norm_arr4})
    # merge both dataframes
    return df.merge(pair_norm,left_index=True, right_index=True).reset_index(drop=True)  
    


def main():

    import time
    start_time = datetime.now()
    arg = cfg.getInstance()
   
    # # define most common in percentage, by default is 15% higher
    active_lexicons = arg.item_prefix.replace(' ', '').split(',')

    # connect to mysql table
    check_database()
        
    table_name = arg.tablename
    
    for onto in active_lexicons:
        print(onto)
        sim_name = [ "sim_resnik", "sim_lin", "sim_jc", "sim_rel", "sim_jac", "sim_islch"]
        
        for s in sim_name:  

            #print(cols_name[count_sim])
            result = get_column('_'.join([table_name,onto]),column= s)
            if len( result ) != 0:
                table_norm = '_'.join(['norm',table_name,onto,s])
                create_norm_table(tablename=table_norm,sim=s)
                result = pd.DataFrame( np.array( result ), columns=['comp_1', 'comp_2',s] )
                df = normalize(result,sim=s)
                #print(df.head(5))
                if not df.empty:
                    # creation of engine to MYSQL database to insert pandas DataFrame in the database
                    save_to_mysql( df=df.drop_duplicates(), table_name=table_norm, name_prefix='' ) 
            
    print('SUCCESSFULLY NORMALIZED!')
    print(f'Duration: {datetime.now() - start_time}')

# ---------------------------------------------------------------------------------------- #

if __name__ == '__main__':
    main()    

