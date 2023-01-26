"""
Most popular algotithm

"""

import pandas as pd
import numpy as np
import csv


def get_n_most_popular(df_train, n):
    n_most_popular = df_train.groupby(['item']).size().reset_index(name='counts').sort_values(by=['counts'],
                                                                                              ascending=False).head(
        n).item

    return n_most_popular


def set_recommendations_by_user(df_test, n_most_pop):
    with open('groundtruth_validation_pop_rec.csv', mode='w') as file:
        writer = csv.writer(file, delimiter=',')

        users = np.unique(df_test.user)

        n_most_pop_list = n_most_pop.to_list()

        for user in users:
            for item in n_most_pop_list:
                writer.writerow([user, item])


def main():
    df_train_path = 'train.csv'
    df_test_path = 'groundtruth_validation.csv'

    df_train = pd.read_csv(df_train_path, names=['user', 'item', 'rating', 'item_name', 'year'])

    df_test = pd.read_csv(df_test_path, names=['user', 'item', 'rating', 'item_name', 'year'])

    n_most_pop = get_n_most_popular(df_train, 10)
    print(df_test)
    set_recommendations_by_user(df_test, n_most_pop)


if __name__ == '__main__':
    main()