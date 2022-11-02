import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from myconfiguration import MyConfiguration as cfg


def get_train_test_random(data, percentage):

    unique_users = np.unique(data.user)
    print('unique users', unique_users)

    step = int(len(unique_users) / (len(unique_users)*percentage))
    print('step', step)
    users_to_select_index = np.arange(0, len(unique_users), step)
    users_to_test = unique_users[users_to_select_index]
    print('test users to', users_to_test, ' ',  users_to_test.shape)

    users_to_train_1 = np.delete(unique_users, users_to_test)
    print('train users to', users_to_train_1)
    data_train_1 = data[data.user.isin(users_to_train_1)]
    print('train users to 2 ', users_to_train_1)

    data_test_1 = data[data.user.isin(users_to_test)]
    data_test = data_test_1.groupby('user').tail(1)
    data_train_2 = pd.concat([data_test_1, data_test]).drop_duplicates(keep=False)
    data_train = pd.concat([data_train_1, data_train_2])

    return data_train, data_test

    
def get_train_test(data, percentage):
    unique_users = np.unique(data.user)
    print('unique users', unique_users.shape)
    print(unique_users)

    step = int(len(unique_users) / (len(unique_users) * percentage))
    users_to_select_index = np.arange(0, len(unique_users), step)
    print('step', step)

    users_to_test = unique_users[users_to_select_index]
    users_to_train_1 = np.delete(unique_users, users_to_test)
    data_train = data[data.user.isin(users_to_train_1)]

    data_test = data[data.user.isin(users_to_test)]

    return data_train, data_test



def get_test_splited(full_test):

    print('Split data into test and validation ...')

    data_test = full_test.groupby('user').tail(1)
    data_test2 = pd.concat([full_test, data_test]).drop_duplicates(keep=False)
    return data_test, data_test2


def save_to_csv(path, data):

    data.to_csv(path, index=False, header=False)


def split_data(data, percentage):
	'''Splits the data set into training, validation and test sets.
	Each user is in one and only one set.
	nb_val_users is the number of users to put in the validation set.
	nb_test_users is the number of users to put in the test set.
	'''
	nb_users = data.user.nunique()

	# check if nb_val_user is specified as a fraction
	nb_test_users = int(round(percentage * nb_users))

	def extract_n_users(df, n):
		users_ids = np.random.choice(df.user.unique(), n)
		n_set = df[df.user.isin(users_ids)]
		remain_set = df.drop(n_set.index)
		return n_set, remain_set

	print('Split data into training and validation ...')
	val_set, train_set = extract_n_users(data, nb_test_users)
	return train_set, val_set


def main():
    
    arg = cfg.getInstance()
    csv_original_path = arg.path_to_cord_ds

    df_file = pd.read_csv(csv_original_path, names=['user', 'item', 'rating', 'item_name', 'year'])
    print(df_file)
    # number of unique users
    # number of unique items
    # number of ratings
    # sparsity 

    # print('n users: ', df_file.user.unique().shape[0])
    # print('n items: ', df_file.item.unique().shape[0])
    #print('n ratings: ', df_file.size)
    #
    # print('sparsity: ', 1 - (df_file.size / (df_file.user.unique().shape[0] * df_file.item.unique().shape[0])))

    df_train, df_test = get_train_test(df_file, 0.2)
    print('first')

    final_train, final_validation = split_data(df_train, .2)

    # # print('second')
    final_test, final_test_users = get_test_splited(df_test)

    # print(final_train)
    # print(final_validation)
    print(final_test_users)
    print(final_test)
    save_to_csv('train.csv', final_train)
    save_to_csv('groundtruth_validation.csv', final_validation)
    save_to_csv('test.csv', final_test_users)
    save_to_csv('groundtruth_test.csv', final_test)


if __name__ == '__main__':
    main()