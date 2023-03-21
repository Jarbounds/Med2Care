# Preparation of data for CORD-19

Guide to reproduce all the work from scratch.

This module allows you to insert the items collected from the previous step - RS-Dataset -, its ancestors, and measure of similarities: structural (chebi) and content information (all) in a mysql database. This is followed by the selection of ancestors from the items with the closest similarity (1st quartile). Obtaining the ancestors of each item is done using a ssmpy function (get_ancestors). The measure of similarities is given by another ssmpy function (light_similarity). Similarities are from Resnik, Lin and Jian and Conrad. New similarity measures are added, such as Schlicker, Jaccard, and Sánchez and Batet. For the chebi ontology, two structural similarities will be computed: Tanimoto and morgan. The input dataset results from previous step of creating the dataset for recommender systems, with the items referred to in the articles. The output dataset contains these plus their closest similarity ancestors.


For our dataset, we only want to include articles with the following characteristics:
- authors' information
- available title
- available body text
- article text expressed in English
- non-duplicate articles

The next step will be apply RS algorithms and evaluations.

---------------------------------------------------------

## Summary
- [1. Run docker shell script](#1)
- [2. Knowledge-Based Recommender Systems](#2)
  - [2.1. MySQL IP address](#2.1)
  - [2.1. Similarity Metrics](#2.2)
  - [2.2. Normalize metrics](#2.3)
  - [2.3. Create final dataset](#2.4)
- [3. Run all process in a shell script](#3)  
- [4. Requirements](#4)
  - [4.1. Libraries](#4.1)

---------------------------------------------------------


# 1. Run docker shell script<a name="1"></a>

You can run a shell script (docker.sh) that will create a docker image and the container. You just need to indicate the name of the docker image and the folder where you will save the results. The container name will be automatically created from the image (ended by ##\_ctr).

```
bash docker.sh <name_of_image> <name_of_data_folder>
```

Provide the execution permission (if needed) to the script by giving command
```
chmod +777 docker.sh
```

# 2. Knowledge Base Recommender Systems<a name="2"></a>

ALL configurations are defined <config.ini>

## 2.1. MySQL IP address<a name="2.1"></a> 

Before creating the final dataset, and because the calculated similarity values are stored in a mysql database, you need to define the IP address in a docker environment.

sudo docker run --detach --name=<NAME_OF_CONTAINER> --env="MYSQL_ROOT_PASSWORD=1234" --publish 6603:3306 --volume=<PATH_OF_MYQSL>/db_mysql:/var/lib/mysql mysql

sudo docker inspect <NAME_OF_CONTAINER> | grep IPAddress

sudo docker exec -it <NAME_OF_CONTAINER> bash

mysql --host=172.17.0.5 --user=root --password=1234 <NAME_OF_BD>

NOTE: <NAME_OF_BD> is defined in config.ini

## 2.2. Similarity Metrics<a name="2.2"></a>

This module calculates the similarity between entities and save the results in a mysql table. The entities exist on the CORD-19 dataset corpus. Moreover, we add their ancestors to improve resullts.

````
python3 calculate_similarity_cord19.py 
````

If the dataset is very (very) large, my advice is to calculate the structural similarity in a separate script. First, you must run the above script, since the input values are stored in the mysql database previously saved in entity_sim_cord19_rs.similarity_chebi.

````
python3 calculate_structural_similarity_cord19.py   
````

## 2.3. Normalize metrics<a name="2.3"></a>

Normalize the values of diferent similarities metrics obtained in calculate_similarity_cord19_recsys_ds.py. Methods are Z-score, Min-Max Scaling, (Modified) Tanh Estimator and Sigmoid Normalization.

````
python3 normalize_similarities.py   
````

## 2.4. Create final dataset<a name=#2.4></a>

This module create CORD-19 corpus dataset with is ancestors as: < user, user_name, item, item_name, rating, year>. The items should be defined by user.

````
python3 create_kbds_cord19.py 
````

# 3. Run all process in a shell script<a name="3"></a>

You can run all the scripts listed above in a single operation, just call the model.sh. By default, the scripts are: (1) calculate_similarity_cord19, (2) calculate_structural_similarity_cord19, (3) normalize_similarities, (4) create_kbds_cord19. You can change it by placing the comment character ('#'). 

```
bash run_process.sh 
```

Provide the execution permission (if needed) to the script by giving command
```
chmod +777 run_process.sh
```

# 4. Requirements<a name="4"></a>

## 4.1. Libraries<a name="4.1"></a>

- pandas
- numpy
- ssmpy
- merpy
- rdflib
- requests
- configargparse
- rdkit-pypi
- bioservices
- scipy
- mysql-connector-python==8.0.11
- pymysql
- sqlalchemy
- scikit-learn