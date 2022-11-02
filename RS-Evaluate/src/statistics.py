import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from myconfiguration import MyConfiguration as cfg


def main():
    
    arg = cfg.getInstance()
    csv_original_path = arg.path_to_cord_ds

    df_file = pd.read_csv(csv_original_path, names=['user', 'item', 'rating', 'item_name', 'year'])

    # number of unique users
    # number of unique items
    # number of ratings
    # sparsity 

    print('n users: ', df_file.user.unique().shape[0])
    print('n items: ', df_file.item.unique().shape[0])
    print('n ratings: ', df_file.size)

    print('sparsity: ', 1 - (df_file.size / (df_file.user.unique().shape[0] * df_file.item.unique().shape[0])))

    # items by ontology

    print("CHEBI items: ", df_file[df_file.item.str.startswith('CHEBI')].item.unique().shape[0])

    print("DOID items: ", df_file[df_file.item.str.startswith('DOID')].item.unique().shape[0])

    # items by user
    #%matplotlib inline

    unique_users = df_file.user.unique()
    items_by_user = df_file.groupby(['user'])["item"].count().reset_index()
    items_by_user = items_by_user.sort_values(by=['item'], ascending=False)
    print(items_by_user)
    items_by_user.user = items_by_user.user.astype('str')

    print('max items by user: ', items_by_user.item.max())
    print('min items by user: ', items_by_user.item.min())
    print('mean items by user: ', items_by_user.item.mean())

    plt.scatter(items_by_user.user, items_by_user.item)
    plt.axhline(y=items_by_user.item.mean(), color='r', linestyle='-')
    plt.ylabel('number of items')
    plt.xlabel('user')
    plt.show()

    # users by item

    unique_items = df_file.item.unique()
    users_by_item = df_file.groupby(['item'])["user"].count().reset_index()
    users_by_item = users_by_item.sort_values(by=['user'], ascending=False)

    print('max users by item: ', users_by_item.user.max())
    list_of_max_items = users_by_item[users_by_item.user == users_by_item.user.max()].item.values
    print(list_of_max_items)

    print(df_file[df_file.item == list_of_max_items[0]])

    print('min users by item: ', users_by_item.user.min())
    print('mean users by item: ', users_by_item.user.mean())

    dataset_doid = df_file[df_file.item.str.startswith('DOID')]
    unique_items_d = dataset_doid.item.unique()
    users_by_item_d = dataset_doid.groupby(['item'])["user"].count().reset_index()
    users_by_item_d = users_by_item_d.sort_values(by=['user'], ascending=False)

    print('max users by item: ', users_by_item_d.user.max())
    list_of_max_items_d = users_by_item_d[users_by_item_d.user == users_by_item_d.user.max()].item.values
    print(list_of_max_items_d)

    print(dataset_doid[dataset_doid.item == list_of_max_items_d[0]])

    print('min users by item: ', users_by_item_d.user.min())
    print('mean users by item: ', users_by_item_d.user.mean())

    dataset_chebi = df_file[df_file.item.str.startswith('CHEBI')]
    unique_items_c = dataset_chebi.item.unique()
    users_by_item_c = dataset_chebi.groupby(['item'])["user"].count().reset_index()
    users_by_item_c = users_by_item_c.sort_values(by=['user'], ascending=False)

    print('max users by item: ', users_by_item_c.user.max())
    list_of_max_items_c = users_by_item_c[users_by_item_c.user == users_by_item_c.user.max()].item.values
    print(list_of_max_items_c)

    print(dataset_chebi[dataset_chebi.item == list_of_max_items_c[0]])

    print('min users by item: ', users_by_item_c.user.min())
    print('mean users by item: ', users_by_item_c.user.mean())


if __name__ == '__main__':
    main()