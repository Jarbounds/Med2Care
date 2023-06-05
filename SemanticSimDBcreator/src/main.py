import os
import ssmpy
import pandas as pd

from calculate_simlarities import calculate_semantic_similarity_chunks
from database import \
    check_database, get_items_ids, create_connection_sqlite, create_engine_mysql, create_table, table_exists
from datetime import datetime
from dataset import upload_dataset
from myconfiguration import MyConfiguration as Config


pd.set_option('display.max_columns', None)

if __name__ == '__main__':
    start_time = datetime.now()
    config: Config = Config.get_instance()

    # connect db
    check_database()

    # read dataset; select the right columns; select items only from ontology
    df_dataset = upload_dataset(
        config.dataset,
        config.item_prefix
    )

    # check ontology database
    if not os.path.isfile(config.path_to_ontology):
        print("Database from owl does not exit. Creating...")
        ssmpy.create_semantic_base(
            config.path_to_owl,
            config.path_to_ontology,
            "http://purl.obolibrary.org/obo/",
            "http://www.w3.org/2000/01/rdf-schema#subClassOf",
            ""
        )
    else:
        print("Database ontology file already exists")

    # get item id in the input dataset
    items_ids = get_items_ids(df_dataset, config.item_prefix)
    print("n of ids: ", items_ids.shape)

    database = config.database
    table_name = config.table_name

    # connection to sqlite database
    conn = create_connection_sqlite(config.path_to_ontology)

    # creation of engine to MYSQL database to insert pandas DataFrame in the database
    engine = create_engine_mysql()

    if not table_exists(database, table_name):
        create_table(database, table_name)

    calculate_semantic_similarity_chunks(
        items_ids,
        conn,
        engine,
        table_name,
        config.n_split,
        config.item_prefix
    )

    # close connection
    conn.close()

    end_time = datetime.now()
    # save meta-information: date, time, database, dataset and ontology label in the txt file
    with open('../info_process.txt', 'a') as f:
        f.write(
            f"Date: {datetime.now()} \nDuration: {end_time - start_time}\n"
        )
        f.write(
            f"Database: {config.database} \nDataset: {config.dataset} \nOntology: {config.item_prefix}\n\n"
        )
        f.close()

    print("FINISHED!")
