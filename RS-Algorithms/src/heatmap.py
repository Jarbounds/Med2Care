import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


max_top = 10
similar = 5

metrics_list = [
    'Precision',
    'Recall',
    'F1-Score',
    'False-Positive Rate',
    'Reciprocal Rank',
    'nDCG',
    'AUC'
]

column_list = [f'top{i}' for i in range(1, max_top + 1)]


def get_files(folder_path):
    for item in os.listdir(folder_path):
        complete_path = f'{folder_path}/{item}'
        if os.path.isfile(complete_path):
            if item.endswith('csv'):
                yield complete_path


def get_metric_name(file_path):
    return file_path.split(f'nsimilar_{similar}_')[-1].split('.')[0]


def get_df(file_path):
    df = pd.read_csv(file_path)
    df = df[column_list]
    return df


def create_df(folder_path, metric_index):
    print(f'Create for folder {folder_path} and metric {metric_index}')
    complete_df = pd.DataFrame([], columns=column_list)
    for file in get_files(folder_path):
        # Create a DataFrame from the data
        if f'nsimilar_{similar}_' not in file:
            continue
        new_index = get_metric_name(file)
        df = get_df(file)
        df = df.iloc[[metric_index]]
        df.rename(index={metric_index: new_index}, inplace=True)
        complete_df = pd.concat([complete_df, df])
    a = [col.replace('top', '') for col in complete_df.columns]
    complete_df.columns = a
    return complete_df


def create_heatmap(df, title, save_file_path=None):
    # Plot the heatmap
    plt.figure(figsize=(6, 7))
    heatmap = sns.heatmap(df.round(2), xticklabels=True, yticklabels=True, annot=True, cmap='BuPu')
    plt.title(title)
    heatmap.xaxis.tick_top()
    if save_file_path is not None:
        plt.savefig(save_file_path, bbox_inches='tight')
    plt.close()


def precision_heatmap(folder_path, save_file_path=None):
    df = create_df(folder_path, 0)
    create_heatmap(df, 'Precision@k', save_file_path)
    return df


def recall_heatmap(folder_path, save_file_path=None):
    df = create_df(folder_path, 1)
    create_heatmap(df, 'Recall@k', save_file_path)
    return df


def mrr_heatmap(folder_path, save_file_path=None):
    df = create_df(folder_path, 4)
    create_heatmap(df, 'MRR@k', save_file_path)
    return df


def ndcg_heatmap(folder_path, save_file_path=None):
    df = create_df(folder_path, 5)
    create_heatmap(df, 'nDCG@k', save_file_path)
    return df


def get_folders(base_path):
    for item in os.listdir(base_path):
        if os.path.isdir(f'{base_path}/{item}'):
            yield item


def main():
    folder = '../mlData/drugbank'
    # folder = '../mlData/emc'
    data_source_folder = folder.split('/')[-1]
    save_folder = f'../data/heatmaps/{data_source_folder}'
    os.makedirs(save_folder, exist_ok=True)

    for dataset_folder in get_folders(folder):
        complete_dataset_path = f'{folder}/{dataset_folder}'
        complete_save_path = f'{save_folder}/{dataset_folder}'

        precision_heatmap(complete_dataset_path, f'{complete_save_path}_precision.pdf')
        recall_heatmap(complete_dataset_path, f'{complete_save_path}_recall.pdf')
        mrr_heatmap(complete_dataset_path, f'{complete_save_path}_mrr.pdf')
        ndcg_heatmap(complete_dataset_path, f'{complete_save_path}_ndcg.pdf')


if __name__ == '__main__':
    main()
