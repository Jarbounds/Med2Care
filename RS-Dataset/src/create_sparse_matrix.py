from numpy import ndarray
from numpy import count_nonzero
import numpy as np
import pandas as pd

df = pd.read_csv('../data/results/comm_subset_medicine_dataset.csv', header=0)

user_unique: ndarray = df['user'].unique()
len_user = user_unique.size

item_unique: ndarray = df['item'].unique()
len_item = item_unique.size

# create dense matrix
# A = np.zeros((len_user, len_item))
A = np.zeros((len_item, len_user))

for _, row in df.iterrows():
    print(row)
    if row.rating == 1:
        ru = row['user']
        ri = row['item']
        idr = np.where(user_unique == ru)[0][0]
        idc = np.where(item_unique == ri)[0][0]
        A[idc][idr] += 1
        # A[idr][idc] += 1

print(A)

print(f'user: {user_unique}')
print(f'item: {item_unique}')

# calculate sparsity
sparsity = 1.0 - (count_nonzero(A) / float(A.size))
print(sparsity)
