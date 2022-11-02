# README #

This module creates a recommendation dataset with the format of < 'user', 'item', 'rating', 'item_name', 'year' > and < 'user', 'author_name' >, where users are authors from research articles, the items are biomedical entities from multi-field ontologies, and
the ratings are the number of articles an author wrote about an item. 



### Requirements: ###
* python > 3
* numpy
* configargparse
* pandas
* scipy
* spacy==3.1.0
* sklearn
* lenskit
* cffi
* unidecode
* unicode
* rdflib
* requests
* metapub==0.5.5
* Bio
* entrezpy==2.1.3
* crossref-commons

### Data: ###
* Original documents: https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge 
* Entities Documents: From https://github.com/lasigeBioTM/knowledge-extraction-from-CORD-19/tree/master/NER


### Running: ###

* configure config file

````
python3 create_cord19_recsys_dataset.py
````

* output: csv file with < 'user', 'item', 'rating', 'item_name', 'year' > columns

### Create a Docker: ###

>> docker build -t <"image_name"> .
>> docker run -t -d --name <container_name> --net=host -v /path/to/SciRec2021-CORD19/ELT:/ELT -v /path/to/SciRec2021-CORD19/RS:/RS [--volumes-from other_container] <image_name>
>> docker exec -it <container_name> bash

cd /config