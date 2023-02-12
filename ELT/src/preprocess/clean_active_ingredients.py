import os


def clean_duplicates(base_dir):
    for file in os.listdir(base_dir):
        file_path = os.path.join(base_dir, file)
        if not os.path.isfile(file_path):
            continue
        with open(file_path, 'r', encoding='utf-8') as fp:
            active_ingredients = [
                ing.rstrip('\n') for ing in fp.readlines()
            ]
        unique = set()
        for ingredient in active_ingredients:
            ingredient = ingredient.lower()
            unique.add(ingredient)
        unique_sorted = sorted(unique)
        with open(file_path, 'w', encoding='utf-8') as fp:
            for ing in unique_sorted:
                fp.write(f'{ing}\n')


def main():
    base_dir = '../../data/active_principles_by_disease'
    clean_duplicates(base_dir)


if __name__ == '__main__':
    main()
