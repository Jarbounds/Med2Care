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
# @email:                                                                     #
# @date: 17 Feb 2021                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#                                                                             #  
# @last update:                                                               #  
#   version 1.1: 31 Mar 2021                                                  #      
#   (author: Matilde Pato, matilde.pato@gmail.com)                            # 
#                                                                             #   
#                                                                             #  
###############################################################################

import unidecode
import numpy as np
import pandas as pd


def get_user_item_rating(list_of_authors, df_entities):
    user_item_rating = []

    for author in list_of_authors:
        for entity in df_entities.entities_id:
            user_item_rating.append([author, entity, 1])

    return user_item_rating


def id_to_index(df):
    """
    maps the values to the lowest consecutive values
    :param df: pandas Dataframe with columns user, item, rating
    :return: pandas Dataframe with the columns index_item and index_user
    """

    index_user = np.arange(0, len(df.user.unique()))

    df_user_index = pd.DataFrame(df.user.unique(), columns=["user"])
    df_user_index["new_index"] = index_user

    df["index_user"] = df["user"].map(df_user_index.set_index('user')["new_index"]).fillna(0)
    # print(df)
    return df


def remove_accents(a):
    return unidecode.unidecode(a.decode('utf-8'))


def remove_accents_from_authors(records_df, column):
    records_df[column] = records_df[column].astype('unicode')
    records_df[column] = records_df[column].str.normalize('NFKD').str.encode('ascii', errors='ignore').str.decode(
        'utf-8')

    # for i in range(records_df[column].size):
    #
    #     for b in range(len(records_df[column][i])):
    #         records_df[column][i][b] = unidecode.unidecode(records_df[column][i][b])

    return records_df
