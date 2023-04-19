import numpy as np
import pandas as pd
from scipy.sparse import coo_matrix


def three_columns_matrix_to_csr(matrix):
    """

    :param matrix: pandas dataframe of user, item, rating
    :return: (item, user) rating sparse matrix
    """

    print(len(matrix.index_item.unique()), len(matrix.index_user.unique()))
    rating = np.array(matrix.rating.astype(int))
    index_item = np.array(matrix.index_item.astype(int))
    index_user = np.array(matrix.index_user.astype(int))
    m = coo_matrix((rating, (index_item, index_user)), dtype=np.int64)
    return m


def save_final_data(data, path_csv):
    """
    Save data to csv file
    :param data: pandas Dataframe with columns <user, item, rating>
    :param path_csv: path to the csv file
    :return
    """
    df = pd.DataFrame.from_dict(data)
    df = df.reindex(sorted(df.columns), axis=1)
    df.to_csv(path_csv)


def id_to_index(df):
    """
    maps the values to the lowest consecutive values
    :param df: pandas Dataframe with columns user, item, rating
    :return: pandas Dataframe with the columns index_item and index_user
    """
    index_item = np.arange(0, len(df.item.unique()))
    index_user = np.arange(0, len(df.user.unique()))

    df_item_index = pd.DataFrame(df.item.unique(), columns=["item"])
    df_item_index["new_index"] = index_item
    df_user_index = pd.DataFrame(df.user.unique(), columns=["user"])
    df_user_index["new_index"] = index_user

    df["index_item"] = df["item"].map(df_item_index.set_index('item')["new_index"]).fillna(0)
    df["index_user"] = df["user"].map(df_user_index.set_index('user')["new_index"]).fillna(0)

    return df, df_item_index, df_user_index
