import os
import numpy as np
import pandas as pd
from dataset import upload_dataset
from pandas import DataFrame
from myconfiguration import MyConfiguration as Config
from lightfm.data import Dataset
from lightfm import LightFM
from lightfm.evaluation import precision_at_k, recall_at_k, reciprocal_rank, auc_score
from sklearn.model_selection import KFold
from recommender_evaluation import fmeasure
from cross_val import calculate_dictionary_mean, add_dict
from data import save_final_data


RANDOM_STATE = 123321


def all_evaluation_metrics_lightfm(model, test_interactions, test_user_features, test_item_features, metrics_dict) -> dict:
    top_k = Config.get_instance().topk

    for k in range(1, top_k + 1):
        precision_eval_metric = precision_at_k(
            model,
            test_interactions,
            k=k,
            user_features=test_user_features,
            item_features=test_item_features
        ).mean()
        recall_eval_metric = recall_at_k(
            model,
            test_interactions,
            k=k,
            user_features=test_user_features,
            item_features=test_item_features
        ).mean()
        reciprocal_rank_eval_metric = reciprocal_rank(
            model,
            test_interactions,
            user_features=test_user_features,
            item_features=test_item_features
        ).mean()
        auc_eval_metric = auc_score(
            model,
            test_interactions,
            user_features=test_user_features,
            item_features=test_item_features
        ).mean()

        f1_score_eval_metric = fmeasure(precision_eval_metric, recall_eval_metric)

        if len(metrics_dict) != k:
            metrics_dict.update(
                {
                    'top' + str(k): [
                        precision_eval_metric,
                        recall_eval_metric,
                        f1_score_eval_metric,
                        -1,
                        reciprocal_rank_eval_metric,
                        -1,
                        auc_eval_metric
                    ]
                }
            )
        else:
            old = np.array(metrics_dict['top' + str(k)])
            new = np.array([
                precision_eval_metric,
                recall_eval_metric,
                f1_score_eval_metric,
                -1,
                reciprocal_rank_eval_metric,
                -1,
                auc_eval_metric
            ])

            to_update = old + new
            metrics_dict.update({'top' + str(k): to_update})

    return metrics_dict


def main():
    config: Config = Config.get_instance()

    dataset_folder = config.dataset_folder
    onto_prefix = config.item_prefix
    top_k = config.topk
    cv_folds = config.cv

    for dataset_file in os.listdir(dataset_folder):
        dataset_path = f'{dataset_folder}/{dataset_file}'
        dataset_csv: DataFrame = pd.read_csv(dataset_path, header=0, sep=',')
        dataset_csv = dataset_csv[['user', 'username', 'item', 'item_name', 'rating']]

        if dataset_csv.dtypes['item'] == object:
            dataset_csv = dataset_csv[dataset_csv['item'].astype(str).str.startswith(onto_prefix)]
            dataset_csv['item'] = dataset_csv['item'].str.replace(onto_prefix, '').astype(int)

        dataset_csv = dataset_csv.loc[dataset_csv['rating'] >= 1]

        dataset: Dataset = Dataset()

        dataset.fit(
            users=(user for user in dataset_csv['user'].values),
            items=(item for item in dataset_csv['item'].values),
            user_features=[
                row['username'] for _, row in dataset_csv.iterrows()
            ],
            item_features=[
                row['item_name'] for _, row in dataset_csv.iterrows()
            ]
        )

        num_users, num_items = dataset.interactions_shape()
        print('Num users: {}, num_items {}.'.format(num_users, num_items))

        (interactions, weights) = dataset.build_interactions(
            data=((row['user'], row['item'], float(row['rating'])) for _, row in dataset_csv.iterrows())
        )

        user_features = dataset.build_user_features(
            [
                (
                    row['user'], [row['username']]
                ) for _, row in dataset_csv.iterrows()
            ]
        )

        item_features = dataset.build_item_features(
            [
                (
                    row['item'], [row['item_name']]
                ) for _, row in dataset_csv.iterrows()
            ]
        )

        model: LightFM = LightFM(
            no_components=150,
            loss='warp',
            k=top_k,
            random_state=RANDOM_STATE
        )

        k_fold = KFold(n_splits=cv_folds, shuffle=True, random_state=RANDOM_STATE)

        total_metrics = {}

        for cv, (train_indices, test_indices) in enumerate(k_fold.split(interactions)):
            train = interactions.tocsr()[train_indices].tocoo()
            test = interactions.tocsr()[test_indices].tocoo()
            split_weights = interactions.tocsr()[train_indices].tocoo()

            model.fit(
                interactions=train,
                sample_weight=split_weights,
                user_features=user_features,
                item_features=item_features
            )

            metrics_dict = {}

            metrics_dict = all_evaluation_metrics_lightfm(
                model,
                test,
                user_features,
                item_features,
                metrics_dict
            )

            total_metrics = add_dict(
                total_metrics,
                metrics_dict,
                cv,
                cv
            )

        total_metrics = calculate_dictionary_mean(total_metrics, cv_folds)

        path = f"../mlData/{dataset_folder.rsplit('/')[-1]}/{dataset_file.rsplit('.')[0]}"
        str_folds = f'/lightfm_results_nfolds{str(cv_folds)}'
        str_n = f'_nsimilar_{str(config.n)}'
        completed_path = f'{path}{str_folds}{str_n}'

        os.makedirs(path, exist_ok=True)

        save_final_data(total_metrics, f'{completed_path}_warp.csv')


if __name__ == '__main__':
    main()
