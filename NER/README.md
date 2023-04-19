# Named Entity Recognition (NER) + Named Entity Linking (NEL)

Guide to reproduce all the work from scratch.

**Goal**: To recognize chemical and disease entities in the retrieved articles and to link them to the respective ontology identifiers.

This module extracts and normalizes entities from the CORD-19 dataset. To perform NER and NEL, we are going to apply Minimal Named-Entity Recognizer [MER](https://pypi.org/project/merpy/) tool.

It opens each json file and runs NER on the title, abstract (if exists), body text and captions, according to the segmentations provided on the original corpus.

Time.sleep is used to add delay in the execution of a program, because of the constant requests to metapub and Bio. In some situations requests are made to pmid or the title of the article.

We are going to use the [Disease Ontology](https://disease-ontology.org/) (DO), and the [Chemical Entities of Biological Interest](https://www.ebi.ac.uk/chebi/) (ChEBI) ontology.

The next step will be created recommender system dataset in RS-Dataset folder.

---------------------------------------------------------

## Summary
- [1. Run docker shell script](#1)
- [2. NER & NEL](#2)
  - [2.1. Multiprocessing](#2.1)
  - [2.2. Batch and multiprocessing](#2.2)
- [3. Requirements](#3)
  - [3.1. Libraries](#3.1)
- [4. Outputs](#4)
- [5. Common Problems](#5)

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

# 2. NER & NEL<a name="2"></a>

## 2.1. Multiprocessing<a name="2.1"></a>

```
python3 mer_entities.py 
```

You must enter your email in utils2pubmed: Entrez.email = <INSERT_YOUR_EMAIL_HERE>

## 2.2. Batch and multiprocessing<a name="2.2"></a>

````
python mer_entities_batch.py
````

Finaly, check that all documents have been properly cataloged with

````
python validate_all.py
````

# 3. Requirements<a name="3"></a>

## 3.1. Libraries<a name="3.1"></a>

- pandas
- tqdm
- merpy
- nltk
- metapub
- Bio
- entrezpy==2.1.3
- langdetect==1.0.8
- configargparse

# 4. Output<a name="4"></a>

Both scripts have the same output, which is a json file for each document with the following structure:
{id,
 entities: {uri: doc_count},
 sections: {section_name:
            [
              [start_index, end_index, entity_string, entity_uri]}
            ]
}

e.g. 

{
    "id": "0a5b8413397c8212cd6582383a0922ccb7b77535",
    "entities": {
        "http://purl.obolibrary.org/obo/DOID_8469": 972,
        "http://purl.obolibrary.org/obo/DOID_552": 347,
        "http://purl.obolibrary.org/obo/DOID_934": 170,
        ...
    },
    "sections": {
        "title": [
            [
                40,
                49,
                "influenza",
                "http://purl.obolibrary.org/obo/DOID_8469"
            ],
       ...
       

Every section except title will have multiple paragraphs, so the value of its dictionary is a list of lists

# 5. Common Problems<a name="5"></a>

First, we recommend to always use this module inside a container (like the one provided inside the module) to avoid most of .

There have been found some problems using the nltk library. Following are some problems and possible solutions.

- Errors related to ssl and certificate verification (observed on macOS)
  - This means that the library cannot verify the machine's certificate. To resolve that execute the following command in terminal
    ```sh
    /Applications/Python 3.10/Install Certificates.command
    ```
    replacing `3.10` with the corresponding installed Python version. This should solve the problem.
