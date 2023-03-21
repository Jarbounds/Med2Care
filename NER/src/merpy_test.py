# import merpy
import json
import re
import os
import merpy

from utils import utils2mer

jsons: list = []

base = '../data/comm_use_subset_entities/medicine_set'

all_words: dict = {}

for file in os.listdir(base):
    with open(f'{base}/{file}', 'r') as fp:
        jsons.append((file, json.load(fp)))

for j in jsons:
    if isinstance(j[1]['therapeutic_indications'], str):
        print('-------------------')
        print(f'file: {j[0]}')
        string = re.sub(r"[^A-Za-z0-9 ]{2,}", " ", j[1]['therapeutic_indications'])
        string = utils2mer.items_in_blacklist(string, 'do')
        string = utils2mer.replace_problematic_chars(string)

        insensitive_regex = re.compile(re.escape('hiv'), re.IGNORECASE)
        string = insensitive_regex.sub('hiv infection', string)

        print(merpy.get_entities(string, 'do'))
        for word in string.split(' '):
            if word not in all_words:
                all_words[word] = 1
            else:
                all_words[word] += 1
        print(string)
        print('-------------------')

sort = {k: v for k, v in sorted(all_words.items(), key=lambda item: item[1], reverse=True)}

for (key, value) in sort.items():
    print(f'word: {key} n: {value}')


