import pandas as pd
import numpy as np
import sys

def reciprocal_rank(groundtruth_test, rec_Test):
    if groundtruth_test in rec_Test:
        position = np.where(rec_Test==groundtruth_test)[0][0]+1
        rr = position / len(rec_Test)
    else:
        rr = 0

    return rr


def main():
    users_recommendations_file = 'groundtruth_validation_pop_rec.csv'
    groundtruth_file = 'groundtruth_validation.csv'

    users_rec = pd.read_csv(users_recommendations_file, names=['user', 'rec'])
    groundtruth = pd.read_csv(groundtruth_file, names=['user', 'item', 'rating', 'item_name', 'year'])
    test_users_ids = np.unique(users_rec.user)

    rr_list = []

    for user in test_users_ids:
        rec_user = users_rec[users_rec.user==user].rec

        groundtruth_user = groundtruth[groundtruth.user==user].item.values[0]

        rr = reciprocal_rank(groundtruth_user, np.array(rec_user))
        rr_list.append(rr)

    MRR = np.mean(np.array(rr_list), dtype=np.float64)

    print('MRR@10 = ', str(round(MRR, 5)))

if __name__ == '__main__':
    main()