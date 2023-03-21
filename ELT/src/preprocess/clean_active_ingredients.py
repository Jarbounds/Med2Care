import os
from ELT.src.utils.utils import load_from_file_lines, save_to_file_lines


def clean_duplicates(base_dir):
    for file in os.listdir(base_dir):
        file_path = os.path.join(base_dir, file)
        if not os.path.isfile(file_path):
            continue
        active_ingredients = load_from_file_lines(file_path)
        unique = set()
        for ingredient in active_ingredients:
            ingredient = ingredient.lower()
            unique.add(ingredient)
        unique_sorted = sorted(unique)
        save_to_file_lines(unique_sorted, file_path)


def main():
    base_dir = '../../data/active_principles_by_disease'
    clean_duplicates(base_dir)


if __name__ == '__main__':
    main()
