# Recommender system data set

Guide to reproduce all the work from scratch.

**Goal**: Create final data set

This module creates a recommendation data set with the format of < 'user', 'item', 'rating', 'item_name', 'year' >, where users are authors ids from research articles, the items are biomedical entities from multi-field ontologies and the items' description, and the ratings are the number of articles an author wrote about an item. 

If the original data set does not contain the author's name, or year, we will look for information through the Metapub and Bio libraries.

Time.sleep is used to add delay in the execution of a program, because of the constant requests to metapub and Bio. In some situations requests are made to pmid or the title of the article.

We are going to use the [Disease Ontology](https://disease-ontology.org/) (DO), and the [Chemical Entities of Biological Interest](https://www.ebi.ac.uk/chebi/) (ChEBI) ontology.

The next step will be to create a second dataset with the ancestors of each item in KB folder.

---------------------------------------------------------

## Summary
- [1. Run docker shell script](#1)
- [2. Create data set](#2)
- [3. Requirements](#3)
  - [3.1. Libraries](#3.1)
- [4. Outputs](#4)  

---------------------------------------------------------

# 1. Run docker shell script<a name="1"></a>

You can run a shell script (docker.sh) that will create a docker image and the container. You just need to indicate the name of the docker image and the folder where you will save the results. The container name will be automatically created from the image (ended by ##\_ctr).

```
bash docker.sh <name_of_image> <name_of_data_folder>
```

Provide the execution permission (if needed) to the script by giving command
```
chmod +777 docker
```

# 2. Create data set <a name="2"></a>

```
python3 create_cord19_recsys_dataset.py 
```

You must enter your email in utils2pubmed: Entrez.email = <INSERT_YOUR_EMAIL_HERE>

# 3. Requirements<a name="3"></a>

## 3.1. Libraries<a name="3.1"></a>

- numpy
- configargparse
- pandas
- scipy
- spacy==3.1.0
- sklearn
- lenskit
- cffi
- unidecode
- unicode
- rdflib
- requests
- metapub==0.5.5
- Bio
- entrezpy==2.1.3
- crossref-commons
- matplotlib

# 4. Output<a name="4"></a>

|         | user   | item         | rating | item_name                         | year |
|---------|--------|--------------|--------|-----------------------------------|------|
| 0       | 0      | DOID_225     | 1      | syndrome                          | 2020 |
| 1       | 0      | DOID_2945    | 1      | severe acute respiratory syndrome | 2020 |
| 2       | 1      | CHEBI_132943 | 1      | aspartate                         | 2012 |
| 3       | 1      | CHEBI_15356  | 1      | cysteine                          | 2012 |
| 4       | 1      | CHEBI_15841  | 1      | polypeptide                       | 2012 |
| ...     | ...    | ...          | ...    | ...                               | ...  |
| 9577659 | 174032 | DOID_225     | 1      | syndrome                          | 2020 |
| 9577660 | 174032 | DOID_2945    | 1      | severe acute respiratory syndrome | 2020 |
| 9577661 | 174032 | DOID_4       | 1      | disease                           | 2020 |
| 9577662 | 174032 | DOID_552     | 1      | pneumonia                         | 2020 |
| 9577663 | 174032 | DOID_9563    | 1      | bronchiectasis                    | 2020 |


Three csv files are saved with

1. < 'user', 'item', 'rating', 'item_name', 'year' >
2. < 'user', 'author_name' >
3. < 'user', 'author_name', 'item', 'rating', 'item_name', 'year' >