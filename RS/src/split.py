import pandas as pd
import numpy as np


def get_train_test_random(data, percentage):

    unique_users = np.unique(data.user)
    print('unique users', unique_users.shape)

    step = int(len(unique_users) / (len(unique_users)*percentage))

    users_to_select_index = np.arange(0, len(unique_users), step)

    users_to_test = unique_users[users_to_select_index]
    users_to_train_1 = np.delete(unique_users, users_to_test)

    data_train_1 = data[data.user.isin(users_to_train_1)]

    data_test_1 = data[data.user.isin(users_to_test)]
    data_test = data_test_1.groupby('user').tail(1)
    data_train_2 = pd.concat([data_test_1, data_test]).drop_duplicates(keep=False)


    data_train = pd.concat([data_train_1, data_train_2])

    return data_train, data_test

def get_train_test(data, percentage):
    unique_users = np.unique(data.user)
    print('unique users', unique_users.shape)

    step = int(len(unique_users) / (len(unique_users) * percentage))
    print("vvv", (len(unique_users) / (len(unique_users) * percentage)))
    print(step)
    users_to_select_index = np.arange(0, len(unique_users), step)
    print('step', step)
    print('test users', users_to_select_index)

    users_to_test = unique_users[users_to_select_index]
    users_to_train_1 = np.delete(unique_users, users_to_test)

    data_train = data[data.user.isin(users_to_train_1)]

    data_test = data[data.user.isin(users_to_test)]

    return data_train, data_test

def get_test_splited(full_test):
    data_test = full_test.groupby('user').tail(1)

    data_test2 = pd.concat([full_test, data_test]).drop_duplicates(keep=False)


    return data_test, data_test2


def save_to_csv(path, data):

    data.to_csv(path, index=False, header=False)


def main():
    csv_original_path = '/data/SciReC2021/comm_subset_cord-19_dataset.csv'
    csv_entities_filtered_path = '/data/SciReC2021/comm_subset_cord-19_dataset_chebi_DB_filtered.csv'

    df_file = pd.read_csv(csv_original_path, names=['user', 'item', 'rating', 'item_name', 'year'])

    df_train, df_test = get_train_test(df_file, 0.2)

    final_train, final_validation = get_train_test_random(df_train, 0.2)

    final_test, final_test_users = get_test_splited(df_test)

    print(final_train)
    print(final_validation)
    print(final_test_users)
    print(final_test)
    save_to_csv('train.csv', final_train)
    save_to_csv('groundtruth_validation.csv', final_validation)
    save_to_csv('test.csv', final_test_users)
    save_to_csv('groundtruth_test.csv', final_test)


if __name__ == '__main__':
    main()