###############################################################################
#                                                                             #
# Licensed under the Apache License, Version 2.0 (the "License"); you may     #
# not use this file except in compliance with the License. You may obtain a   #
# copy of the License at http://www.apache.org/licenses/LICENSE-2.0           #
#                                                                             #
# Unless required by applicable law or agreed to in writing, software         #
# distributed under the License is distributed on an "AS IS" BASIS,           #
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.    #
# See the License for the specific language governing permissions and         #
# limitations under the License.                                              #
#                                                                             #
###############################################################################
#                                                                             #  
# @author: Márcia Barros                                                      #  
# @email: marcia.c.a.barros@gmail.com                                         #
# @date: 28 Jan 2020                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 12 Feb 2021                                                  #      
#  (author: Matilde Pato, matilde.pato@gmail.com)                             #  
#                                                                             #  
#  Note:                                                                      #  
# 1. You must to configure dataset.py for your problem                        #  
#                                                                             #
# 2. If is an HPO then the comp_1 and comp_2 for the similarity semantic DB   #
# is represented in string format, elsewhere is in int type                   #   
#                                                                             #  
###############################################################################
#

import os
import ssmpy
import numpy as np
import pandas as pd

import sys
if os.path.isdir( "DiShIn" ):
    pass
sys.path.insert( 1, '/KB/src/DiShIn/sspmy/' )

from Utils.utils2database import check_database, create_connection_sqlite, create_engine_mysql, save_to_mysql

pd.set_option( 'display.max_columns', None )

# ---------------------------------------------------------------------------------------- #

def calculate_semantic_similarity_chunks(entry_ids, ancestor_ids, name_prefix ):
    """

    :param entry_ids: list of entries ids
    :param conn: connection object to sqlite
    :param engine: connection to engine object
    :param table_name: name of the table where the data are saved
    :param n_split: number to split the list of entities
    :param n_split: int
    :param name_prefix: Prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    :return:
    """
    
    # if we consider HPO then we must transform to a string because of the
    # '0000000' format (i.e. 7 digits)
    if name_prefix == 'HP_':
        entry_ids = '0000000'+entry_ids
        ancestor_ids = [f'{s:07d}' for s in ancestor_ids]    

    entry_ids = name_prefix + entry_ids
    ancestor_ids = [name_prefix + str(s) for s in ancestor_ids]    
             
    results = ssmpy.light_similarity( conn, entry_ids, ancestor_ids, "all", 20 )
    newest = [item for items in results for item in items]
    sim_df = pd.DataFrame( newest, columns=["comp_1", "comp_2", "sim_resnik", "sim_lin", "sim_jc"] )
            
            save_to_mysql( sim_df, engine, table_name, name_prefix )

        mask = np.where( aux_array == i )
        aux_array = np.delete( aux_array, mask )





    # ---------------------------------------------------------------------------------------- #
    # connect db
    check_database()

    # ---------------------------------------------------------------------------------------- #
   
    # get item id in the input dataset
    items_ids = get_items_ids(df_dataset, cfg.get_instance().item_prefix)
    print( "n of ids: ", items_ids.shape )
    
    # ---------------------------------------------------------------------------------------- #

    # connection to sqlite database
    conn = create_connection_sqlite(get_db_path)

    # ---------------------------------------------------------------------------------------- #

    # creation of engine to MYSQL database to insert pandas DataFrame in the database
    engine = create_engine_mysql()

    # ---------------------------------------------------------------------------------------- #

    calculate_semantic_similarity_chunks( items_ids, conn, engine, "similarity", item_prefix )

    # ---------------------------------------------------------------------------------------- #
    # close connection
    conn.close()
