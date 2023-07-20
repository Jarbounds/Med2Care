import numpy as np
from lightfm.datasets import fetch_movielens
from lightfm import LightFM
from lightfm.evaluation import precision_at_k


def sample_recommendation(model, data, user_ids):
    train = data['train']
    train_csr = train.tocsr()
    item_labels = data['item_labels']

    n_users, n_items = data['train'].shape

    for user_id in user_ids:
        known_positives = item_labels[train_csr[user_id].indices]

        scores = model.predict(user_id, np.arange(n_items))
        top_items = item_labels[np.argsort(-scores)]

        print(f'User {user_id}')

        print('\tKnown positives')
        for positive in known_positives[:3]:
            print(f'\t\t{positive}')

        print('\tRecommend')
        for recommendation in top_items[:3]:
            print(f'\t\t{recommendation}')


def main():
    data = fetch_movielens(min_rating=5.0)

    train = data['train']
    test = data['test']

    print('Printing train:')
    print(train)
    print()
    print('Printing test:')
    print(test)

    model: LightFM = LightFM(loss='warp')
    model.fit(train, epochs=30, num_threads=2)

    train_precision = precision_at_k(model, train, k=5).mean()
    test_precision = precision_at_k(model, test, k=5).mean()

    print(f'Train precision: {train_precision:.2f}')
    print(f'Test precision: {test_precision:.2f}')

    sample_recommendation(model, data, [3, 25, 450])


if __name__ == '__main__':
    main()
