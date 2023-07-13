import pandas as pd


def main():
    pd.set_option('display.max_columns', 10)
    pd.set_option('display.max_rows', 1000)
    df = pd.read_csv("../data/datasets/drugbank/comm_subset_medicine_dataset.csv", header=0)
    col_list = list(df.columns)
    user, item = col_list.index('user'), col_list.index('item')
    username, item_name = col_list.index('username'), col_list.index('item_name')
    col_list[item], col_list[user] = col_list[user], col_list[item]
    col_list[item_name], col_list[username] = col_list[username], col_list[item_name]
    df = df[col_list]
    df.rename(columns={'user': 'item', 'username': 'item_name', 'item': 'user', 'item_name': 'username'}, inplace=True)
    df.to_csv('../data/comm_subset_medicine_dataset.csv', header=True, index=False, sep=',')


if __name__ == '__main__':
    main()
