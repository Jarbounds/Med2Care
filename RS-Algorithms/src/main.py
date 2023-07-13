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
# @author Matilde Pato                                                        #  
# @email: matilde.pato@isel.pt                                                #
# @date: February, 12th 2021                                                  #
# @version: 1.0                                                               #  
# @last update:                                                               #   
#                                                                             #  
#                                                                             #  
###############################################################################
#

import os

import numpy as np
import ssmpy
from myconfiguration import MyConfiguration as Config
from data import id_to_index, three_columns_matrix_to_csr, save_final_data
from algorithms import get_evaluation
from cross_val import \
    get_shuffle_items, \
    get_shuffle_users, \
    prepare_train_test, \
    check_items_in_model, \
    add_dict, \
    calculate_dictionary_mean
from datetime import datetime
from database import check_database
from dataset import upload_dataset

np.random.seed(42)


def get_dataset_parts(dataset_file: str):
    config: Config = Config.get_instance()

    # get the dataset in <user, item, rating> format
    ratings_original = upload_dataset(
        csv_path=f'{config.dataset_folder}/{dataset_file}',
        name_prefix=config.item_prefix
    )

    ratings, original_item_id, original_user_id = id_to_index(ratings_original)  # are not unique

    users_size = len(ratings.index_user.unique())
    items_size = len(ratings.index_item.unique())
    shuffle_users = get_shuffle_users(ratings)
    shuffle_items = get_shuffle_items(ratings)

    return ratings, original_item_id, original_user_id, users_size, items_size, shuffle_users, shuffle_items


def get_metrics_dictionaries(n_ontology_sim_metric: int, n_rec_algorithms: int, n_metrics: int):
    total_dicts = n_ontology_sim_metric + n_rec_algorithms + (n_rec_algorithms * n_ontology_sim_metric * n_metrics)

    return tuple({} for _ in range(total_dicts))


def evaluate_dataset(config: Config, dataset_file: str):
    print(f'Evaluating dataset {dataset_file}')
    cv_folds = config.cv
    n = config.n
    dataset_folder = config.dataset_folder.rsplit('/')[-1]
    count_cv = 0

    ratings, \
        original_item_id, \
        original_user_id, \
        users_size, \
        items_size, \
        shuffle_users, \
        shuffle_items = get_dataset_parts(dataset_file)

    all_onto_lin, all_onto_resnik, all_onto_jc, all_als, all_bpr, \
        all_als_onto_lin_m1, all_als_onto_resnik_m1, all_als_onto_jc_m1, \
        all_bpr_onto_lin_m1, all_bpr_onto_resnik_m1, all_bpr_onto_jc_m1, \
        all_als_onto_lin_m2, all_als_onto_resnik_m2, all_als_onto_jc_m2, \
        all_bpr_onto_lin_m2, all_bpr_onto_resnik_m2, all_bpr_onto_jc_m2, \
        all_als_onto_lin_m3, all_als_onto_resnik_m3, all_als_onto_jc_m3, \
        all_bpr_onto_lin_m3, all_bpr_onto_resnik_m3, all_bpr_onto_jc_m3, \
        all_als_onto_lin_m4, all_als_onto_resnik_m4, all_als_onto_jc_m4, \
        all_bpr_onto_lin_m4, all_bpr_onto_resnik_m4, all_bpr_onto_jc_m4 = get_metrics_dictionaries(
            n_ontology_sim_metric=3,
            n_rec_algorithms=2,
            n_metrics=4
        )

    for test_users in np.array_split(shuffle_users, cv_folds):
        test_users_size = len(test_users)
        print("number of test users: ", test_users_size)

        count_cv_items = 0
        for test_items in np.array_split(shuffle_items, cv_folds):
            # models to be used
            test_items_size = len(test_items)
            print("number of test items: ", test_items_size)

            # prepare the data for implicit models
            ratings_test, ratings_train = prepare_train_test(ratings, test_users, test_items)

            test_items = check_items_in_model(ratings_train.index_item.unique(), test_items)
            ratings_sparse = three_columns_matrix_to_csr(ratings_train)  # item, user, rating

            onto_lin, onto_resnik, onto_jc, als, bpr, \
                als_onto_lin_m1, als_onto_resnik_m1, als_onto_jc_m1, \
                bpr_onto_lin_m1, bpr_onto_resnik_m1, bpr_onto_jc_m1, \
                als_onto_lin_m2, als_onto_resnik_m2, als_onto_jc_m2, \
                bpr_onto_lin_m2, bpr_onto_resnik_m2, bpr_onto_jc_m2, \
                als_onto_lin_m3, als_onto_resnik_m3, als_onto_jc_m3, \
                bpr_onto_lin_m3, bpr_onto_resnik_m3, bpr_onto_jc_m3, \
                als_onto_lin_m4, als_onto_resnik_m4, als_onto_jc_m4, \
                bpr_onto_lin_m4, bpr_onto_resnik_m4, bpr_onto_jc_m4 = get_evaluation(
                    test_users,
                    test_users_size,
                    count_cv,
                    count_cv_items,
                    ratings_test,
                    ratings_sparse,
                    test_items,
                    ratings,
                    original_item_id,
                    config.sim_metric
                )

            param_tuple = (count_cv, count_cv_items)

            # add to dictionary
            all_als = add_dict(
                all_als,
                als,
                *param_tuple
            )
            all_bpr = add_dict(
                all_bpr,
                bpr,
                *param_tuple
            )

            if config.sim_metric in ('sim_lin', 'all'):
                all_onto_lin = add_dict(
                    all_onto_lin,
                    onto_lin,
                    *param_tuple
                )
                all_als_onto_lin_m1 = add_dict(
                    all_als_onto_lin_m1,
                    als_onto_lin_m1,
                    *param_tuple
                )
                all_bpr_onto_lin_m1 = add_dict(
                    all_bpr_onto_lin_m1,
                    bpr_onto_lin_m1,
                    *param_tuple
                )

                all_als_onto_lin_m2 = add_dict(
                    all_als_onto_lin_m2,
                    als_onto_lin_m2,
                    *param_tuple
                )
                all_bpr_onto_lin_m2 = add_dict(
                    all_bpr_onto_lin_m2,
                    bpr_onto_lin_m2,
                    *param_tuple
                )

                all_als_onto_lin_m3 = add_dict(
                    all_als_onto_lin_m3,
                    als_onto_lin_m3,
                    *param_tuple
                )
                all_bpr_onto_lin_m3 = add_dict(
                    all_bpr_onto_lin_m3,
                    bpr_onto_lin_m3,
                    *param_tuple
                )

                all_als_onto_lin_m4 = add_dict(
                    all_als_onto_lin_m4,
                    als_onto_lin_m4,
                    *param_tuple
                )
                all_bpr_onto_lin_m4 = add_dict(
                    all_bpr_onto_lin_m4,
                    bpr_onto_lin_m4,
                    *param_tuple
                )

            if config.sim_metric in ('sim_resnik', 'all'):
                all_onto_resnik = add_dict(
                    all_onto_resnik,
                    onto_resnik,
                    *param_tuple
                )
                all_als_onto_resnik_m1 = add_dict(
                    all_als_onto_resnik_m1,
                    als_onto_resnik_m1,
                    *param_tuple
                )
                all_bpr_onto_resnik_m1 = add_dict(
                    all_bpr_onto_resnik_m1,
                    bpr_onto_resnik_m1,
                    *param_tuple
                )

                all_als_onto_resnik_m2 = add_dict(
                    all_als_onto_resnik_m2,
                    als_onto_resnik_m2,
                    *param_tuple
                )
                all_bpr_onto_resnik_m2 = add_dict(
                    all_bpr_onto_resnik_m2,
                    bpr_onto_resnik_m2,
                    *param_tuple
                )

                all_als_onto_resnik_m3 = add_dict(
                    all_als_onto_resnik_m3,
                    als_onto_resnik_m3,
                    *param_tuple
                )
                all_bpr_onto_resnik_m3 = add_dict(
                    all_bpr_onto_resnik_m3,
                    bpr_onto_resnik_m3,
                    *param_tuple
                )

                all_als_onto_resnik_m4 = add_dict(
                    all_als_onto_resnik_m4,
                    als_onto_resnik_m4,
                    *param_tuple
                )
                all_bpr_onto_resnik_m4 = add_dict(
                    all_bpr_onto_resnik_m4,
                    bpr_onto_resnik_m4,
                    *param_tuple
                )

            if config.sim_metric in ('sim_jc', 'all'):
                all_onto_jc = add_dict(
                    all_onto_jc,
                    onto_jc,
                    *param_tuple
                )
                all_als_onto_jc_m1 = add_dict(
                    all_als_onto_jc_m1,
                    als_onto_jc_m1,
                    *param_tuple
                )
                all_bpr_onto_jc_m1 = add_dict(
                    all_bpr_onto_jc_m1,
                    bpr_onto_jc_m1,
                    *param_tuple
                )

                all_als_onto_jc_m2 = add_dict(
                    all_als_onto_jc_m2,
                    als_onto_jc_m2,
                    *param_tuple
                )
                all_bpr_onto_jc_m2 = add_dict(
                    all_bpr_onto_jc_m2,
                    bpr_onto_jc_m2,
                    *param_tuple
                )

                all_als_onto_jc_m3 = add_dict(
                    all_als_onto_jc_m3,
                    als_onto_jc_m3,
                    *param_tuple
                )
                all_bpr_onto_jc_m3 = add_dict(
                    all_bpr_onto_jc_m3,
                    bpr_onto_jc_m3,
                    *param_tuple
                )

                all_als_onto_jc_m4 = add_dict(
                    all_als_onto_jc_m4,
                    als_onto_jc_m4,
                    *param_tuple
                )
                all_bpr_onto_jc_m4 = add_dict(
                    all_bpr_onto_jc_m4,
                    bpr_onto_jc_m4,
                    *param_tuple
                )
            count_cv_items += 1
        count_cv += 1

    # calculates mean and save to a csv file all metrics: [P, R, F, fpr, rr, nDCG, auc] (preference order)
    path = f"../mlData/{dataset_folder}/{dataset_file.rsplit('.')[0]}"
    str_folds = f'/results_nfolds{str(cv_folds)}'
    str_n = f'_nsimilar_{str(n)}'
    completed_path = f'{path}{str_folds}{str_n}'
    floated_folds = float(cv_folds * cv_folds)

    os.makedirs(path, exist_ok=True)

    all_als = calculate_dictionary_mean(all_als, floated_folds)
    all_bpr = calculate_dictionary_mean(all_bpr, floated_folds)

    save_final_data(all_als, f'{completed_path}_ALS.csv')
    save_final_data(all_bpr, f'{completed_path}_BPR.csv')

    if config.sim_metric in ('sim_lin', 'all'):
        all_onto_lin = calculate_dictionary_mean(all_onto_lin, floated_folds)

        all_als_onto_lin_m1 = calculate_dictionary_mean(all_als_onto_lin_m1, floated_folds)
        all_bpr_onto_lin_m1 = calculate_dictionary_mean(all_bpr_onto_lin_m1, floated_folds)

        all_als_onto_lin_m2 = calculate_dictionary_mean(all_als_onto_lin_m2, floated_folds)
        all_bpr_onto_lin_m2 = calculate_dictionary_mean(all_bpr_onto_lin_m2, floated_folds)

        all_als_onto_lin_m3 = calculate_dictionary_mean(all_als_onto_lin_m3, floated_folds)
        all_bpr_onto_lin_m3 = calculate_dictionary_mean(all_bpr_onto_lin_m3, floated_folds)

        all_als_onto_lin_m4 = calculate_dictionary_mean(all_als_onto_lin_m4, floated_folds)
        all_bpr_onto_lin_m4 = calculate_dictionary_mean(all_bpr_onto_lin_m4, floated_folds)

        save_final_data(all_onto_lin, f'{completed_path}_onto_lin.csv')

        save_final_data(all_als_onto_lin_m1, f'{completed_path}_als_onto_lin_m1.csv')
        save_final_data(all_bpr_onto_lin_m1, f'{completed_path}_bpr_onto_lin_m1.csv')

        save_final_data(all_als_onto_lin_m2, f'{completed_path}_als_onto_lin_m2.csv')
        save_final_data(all_bpr_onto_lin_m2, f'{completed_path}_bpr_onto_lin_m2.csv')

        save_final_data(all_als_onto_lin_m3, f'{completed_path}_als_onto_lin_m3.csv')
        save_final_data(all_bpr_onto_lin_m3, f'{completed_path}_bpr_onto_lin_m3.csv')

        save_final_data(all_als_onto_lin_m4, f'{completed_path}_als_onto_lin_m4.csv')
        save_final_data(all_bpr_onto_lin_m4, f'{completed_path}_bpr_onto_lin_m4.csv')

    if config.sim_metric in ('sim_resnik', 'all'):
        all_onto_resnik = calculate_dictionary_mean(all_onto_resnik, floated_folds)

        all_als_onto_resnik_m1 = calculate_dictionary_mean(all_als_onto_resnik_m1, floated_folds)
        all_bpr_onto_resnik_m1 = calculate_dictionary_mean(all_bpr_onto_resnik_m1, floated_folds)

        all_als_onto_resnik_m2 = calculate_dictionary_mean(all_als_onto_resnik_m2, floated_folds)
        all_bpr_onto_resnik_m2 = calculate_dictionary_mean(all_bpr_onto_resnik_m2, floated_folds)

        all_als_onto_resnik_m3 = calculate_dictionary_mean(all_als_onto_resnik_m3, floated_folds)
        all_bpr_onto_resnik_m3 = calculate_dictionary_mean(all_bpr_onto_resnik_m3, floated_folds)

        all_als_onto_resnik_m4 = calculate_dictionary_mean(all_als_onto_resnik_m4, floated_folds)
        all_bpr_onto_resnik_m4 = calculate_dictionary_mean(all_bpr_onto_resnik_m4, floated_folds)

        save_final_data(all_onto_resnik, f'{completed_path}_onto_resnik.csv')

        save_final_data(all_als_onto_resnik_m1, f'{completed_path}_als_onto_resnik_m1.csv')
        save_final_data(all_bpr_onto_resnik_m1, f'{completed_path}_bpr_onto_resnik_m1.csv')

        save_final_data(all_als_onto_resnik_m2, f'{completed_path}_als_onto_resnik_m2.csv')
        save_final_data(all_bpr_onto_resnik_m2, f'{completed_path}_bpr_onto_resnik_m2.csv')

        save_final_data(all_als_onto_resnik_m3, f'{completed_path}_als_onto_resnik_m3.csv')
        save_final_data(all_bpr_onto_resnik_m3, f'{completed_path}_bpr_onto_resnik_m3.csv')

        save_final_data(all_als_onto_resnik_m4, f'{completed_path}_als_onto_resnik_m4.csv')
        save_final_data(all_bpr_onto_resnik_m4, f'{completed_path}_bpr_onto_resnik_m4.csv')

    if config.sim_metric in ('sim_jc', 'all'):
        all_onto_jc = calculate_dictionary_mean(all_onto_jc, floated_folds)

        all_als_onto_jc_m1 = calculate_dictionary_mean(all_als_onto_jc_m1, floated_folds)
        all_bpr_onto_jc_m1 = calculate_dictionary_mean(all_bpr_onto_jc_m1, floated_folds)

        all_als_onto_jc_m2 = calculate_dictionary_mean(all_als_onto_jc_m2, floated_folds)
        all_bpr_onto_jc_m2 = calculate_dictionary_mean(all_bpr_onto_jc_m2, floated_folds)

        all_als_onto_jc_m3 = calculate_dictionary_mean(all_als_onto_jc_m3, floated_folds)
        all_bpr_onto_jc_m3 = calculate_dictionary_mean(all_bpr_onto_jc_m3, floated_folds)

        all_als_onto_jc_m4 = calculate_dictionary_mean(all_als_onto_jc_m4, floated_folds)
        all_bpr_onto_jc_m4 = calculate_dictionary_mean(all_bpr_onto_jc_m4, floated_folds)

        save_final_data(all_onto_jc, f'{completed_path}_onto_jc.csv')

        save_final_data(all_als_onto_jc_m1, f'{completed_path}_als_onto_jc_m1.csv')
        save_final_data(all_bpr_onto_jc_m1, f'{completed_path}_bpr_onto_jc_m1.csv')

        save_final_data(all_als_onto_jc_m2, f'{completed_path}_als_onto_jc_m2.csv')
        save_final_data(all_bpr_onto_jc_m2, f'{completed_path}_bpr_onto_jc_m2.csv')

        save_final_data(all_als_onto_jc_m3, f'{completed_path}_als_onto_jc_m3.csv')
        save_final_data(all_bpr_onto_jc_m3, f'{completed_path}_bpr_onto_jc_m3.csv')

        save_final_data(all_als_onto_jc_m4, f'{completed_path}_als_onto_jc_m4.csv')
        save_final_data(all_bpr_onto_jc_m4, f'{completed_path}_bpr_onto_jc_m4.csv')


def main():
    start_time = datetime.now()

    config: Config = Config.get_instance()

    # check ontology database
    if os.path.isfile(config.path_to_ontology):
        print("Database ontology file already exists")
    else:
        print("Database from owl does not exit. Creating...")
        ssmpy.create_semantic_base(
            config.path_to_owl,
            config.path_to_ontology,
            "http://purl.obolibrary.org/obo/",
            "http://www.w3.org/2000/01/rdf-schema#subClassOf",
            ""
        )

    # connect db
    check_database()

    dataset_folder = config.dataset_folder
    for dataset_file in os.listdir(dataset_folder):
        evaluate_dataset(config, dataset_file)

    # save time process
    end_time = datetime.now()
    with open('../info_process.txt', 'a') as f:
        f.write("Date: {date} \nDuration: {duration}\n".format(
            date=datetime.now(),
            duration=end_time - start_time)
        )
        f.write("Database: {db} \nDataset: {ds} \nOntology: {onto}\n\n".format(
            db=config.database,
            ds=config.dataset_folder,
            onto=config.item_prefix
        ))


if __name__ == '__main__':
    main()
