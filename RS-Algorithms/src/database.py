import pandas as pd
from pandas import DataFrame
import numpy as np
from itertools import product

from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from sqlalchemy import create_engine
import mysql.connector
import sqlite3
from sqlite3 import Error
from myconfiguration import MyConfiguration as Config


def create_default_connection_mysql():
    """
    create a default connection to the mysql database
        specified by host, user and password defined in configurations.ini
    :param
    :return: Connection object
    """
    conf = Config.get_instance()
    assert isinstance(conf.password, object)
    my_db = mysql.connector.connect(
        host=conf.host,
        port=conf.port,
        user=conf.user,
        password=conf.password,
        # ssl_disabled=True,
    )
    return my_db


def create_connection_mysql():
    """ create a connection to the mysql database
       specified by host, user, password and
       database name defined in configurations.ini
   :param
   :return: Connection object
   """
    my_db = create_default_connection_mysql()
    my_db.database = Config.get_instance().database

    return my_db


def create_connection_sqlite(sb_file):
    """
    Create a database connection to the SQLite database
    specified by sb_file
    :param sb_file: sqlite database filename
    :type sb_file: string
    :return: Connection object or None
    """
    try:
        conn = sqlite3.connect(sb_file)
        return conn
    except Exception as e:
        print(e)

    return None


def create_engine_mysql():
    """
    Create a pool and dialect together connection to provide a source of database
    and behavior
    :param:
    :return: Connection engine
    """
    # in case of connection error, change the host as in the next commented code
    conf = Config.get_instance()
    host = conf.host
    user = conf.user
    password = conf.password
    db_name = conf.database

    return create_engine(
        "mysql+pymysql://{user}:{pw}@{host}/{db}".format(
            user=user,
            pw=password,
            host=host,
            db=db_name
        ),
        pool_pre_ping=True
    )


def check_database():
    """
    check the existence of a database with the name defined in configurations.ini
    if none, a new is created as well as a table of similarity
    :param: none
    :return:
    """
    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        check = False
        my_db = create_default_connection_mysql()

        my_cursor = my_db.cursor()

        db_name = Config.get_instance().database

        my_cursor.execute("SHOW DATABASES;")
        for database_tuple in my_cursor:
            # database_tuple = database_tuple[0].decode("unicode-escape")
            # decode was giving an error (note: decode is needed when using mysql docker)
            database_name: str = database_tuple[0]
            if database_name == db_name:
                # x[0].encode().decode('utf-8') == db_name:
                check = True

        if check:
            print("Database already exists")
        else:
            print("Will create database")
            my_cursor.execute("CREATE DATABASE " + db_name)
            create_table()
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_db is not None and my_db.is_connected():
            if my_cursor is not None:
                my_cursor.close()
            my_db.close()


def create_table():
    """
    create a table named similarity with id, comp_1, comp_2,
        sim_resnik, sim_lin, sim_jc as columns in mysql
    :param: none
    :return:
    """
    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        my_db = create_connection_mysql()
        my_cursor = my_db.cursor()

        my_cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        my_cursor.execute("DROP TABLE IF EXISTS `similarity`")

        my_cursor.execute(
            " CREATE TABLE `similarity` (`id` INT NOT NULL AUTO_INCREMENT, `comp_1` INT NOT NULL,  `comp_2` INT NOT NULL, "
            "`sim_resnik` FLOAT NOT NULL, `sim_lin` FLOAT NOT NULL, `sim_jc` FLOAT NOT NULL, PRIMARY KEY (`id`), "
            "INDEX sim (`comp_1`,`comp_2`) ) ENGINE = InnoDB")

        my_cursor.execute("SET FOREIGN_KEY_CHECKS = 1")

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_db.is_connected():
            my_cursor.close()
            my_db.close()


def insert_row(it1, it2, sim_res, sim_l, sim_j):
    """
    insert rows in a similarity table with the corresponding values
    :param it1: entity 1 (id)
    :param it2: entity 2 (id)
    :param sim_res: Resnik semantic similarity
    :param sim_l: Lin's semantic similarity
    :param sim_j: Jiang and Conrath's semantic similarity
    :return:
    """

    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        my_db = create_connection_mysql()

        my_cursor = my_db.cursor()

        sql = "INSERT INTO similarity (comp_1, comp_2, sim_resnik, sim_lin, sim_jc) VALUES (%s,%s,%s,%s,%s)"

        val = (it1, it2, sim_res, sim_l, sim_j)
        my_cursor.execute(sql, val)

        my_db.commit()
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_db.is_connected():
            my_cursor.close()
            my_db.close()


def get_sim_where_comp(it1, it2):
    """
    Get similarity between it1 and it2
    :param it1: entity 1 (id)
    :param it2: entity 2 (id)
    """
    my_db: MySQLConnection | None = None
    my_cursor = None
    len_my_cursor = 0
    try:
        create_engine_mysql()
        my_db = create_connection_mysql()

        my_cursor = my_db.cursor()
        sql = "select * from similarity where comp_1 = %s and comp_2 = %s"
        sql = sql % (it1, it2)
        my_cursor.execute(sql)

        my_cursor = my_cursor.fetchall()
        len_my_cursor = len(my_cursor)

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_db.is_connected():
            my_cursor.close()
            my_db.close()

    return len_my_cursor


def check_if_pair_exist(it1, it2):
    """
    Check if similarity between ontology list exist
    :param it1: entity 1 (id)
    :param it2: entity 2 (id)
    :return: true or false
    """
    print(it1, it2)

    exist = get_sim_where_comp(it1, it2)
    exist_reverse = get_sim_where_comp(it2, it1)
    if exist == 0 and exist_reverse == 0:
        return False
    else:
        return True


def get_items_ids(dataset, name_prefix):
    """
    :param dataset: dataset
    :param name_prefix: Prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    """
    dataset.item = dataset.item.map(lambda x: x.lstrip(name_prefix)).astype(int)
    ids = dataset.item.unique()

    return ids


def confirm_all_test_train_similarities(list1, list2, pairs_from_db):
    # check if all item-item pair was found in the database

    lists_combinations = DataFrame(
        list(product(list1, list2)),
        columns=['l1', 'l2']
    )

    ss = lists_combinations.l1.isin(
        pairs_from_db.comp_1.astype('int64').tolist()) & lists_combinations.l2.isin(
        pairs_from_db.comp_2.astype('int64').tolist())

    ss2 = lists_combinations.l2.isin(
        pairs_from_db.comp_1.astype('int64').tolist()) & lists_combinations.l1.isin(
        pairs_from_db.comp_2.astype('int64').tolist())

    not_found_in_db = lists_combinations[(~ss) & (~ss2)]

    not_found_list_1 = not_found_in_db.l1.unique().tolist()
    not_found_list_2 = not_found_in_db.l2.unique().tolist()

    return not_found_list_1, not_found_list_2


def get_sims(entry_ids_1, entry_ids_2):
    """
    Return <id, comp_1, comp_2> from database between 2 list of entries
    :param entry_ids_1: list of entries 1
    :param entry_ids_2: list of entries 2
    :return result: pandas Dataframe
    """
    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        my_db = create_connection_mysql()
        my_cursor = my_db.cursor()

        format_strings1 = ','.join(['%s'] * len(entry_ids_1))
        format_strings2 = ','.join(['%s'] * len(entry_ids_2))
        sql = "select id, comp_1, comp_2 from similarity where comp_1 in (%s) and comp_2 in (%s)"
        format_strings1 = format_strings1 % tuple(entry_ids_1)
        format_strings2 = format_strings2 % tuple(entry_ids_2)
        sql = sql % (format_strings1, format_strings2)

        my_cursor.execute(sql)

        result = my_cursor.fetchall()

        if len(result) != 0:
            result = DataFrame(
                np.array(result),
                columns=['id', 'comp_1', 'comp_2']
            )
        else:
            result = DataFrame(columns=['id', 'comp_1', 'comp_2'])
        return result
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


def get_read_all(entry_ids_1, entry_ids_2):
    """
    Return all columns from database between 2 list of entries
    :param entry_ids_1: list of entries 1
    :param entry_ids_2: list of entries 2
    :return result: pandas Dataframe
    """
    my_db: MySQLConnection | None = None
    list1 = entry_ids_1.tolist()
    list2 = entry_ids_2.tolist()
    try:
        my_db = create_connection_mysql()

        format_strings1 = ','.join(['%s'] * len(list1))
        format_strings2 = ','.join(['%s'] * len(list2))
        sql = "select * from similarity_chebi where comp_1 in (%s) and comp_2 in (%s)"
        format_strings1 = format_strings1 % tuple(list1)
        format_strings2 = format_strings2 % tuple(list2)
        sql = sql % (format_strings1, format_strings2)

        return pd.read_sql_query(sql, con=my_db)
    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_db is not None and my_db.is_connected():
            my_db.close()


def save_to_mysql(df, engine, table_name, name_prefix):
    """
    :param df: pandas Dataframe
    :param engine: engine object
    :param table_name: name of table where results are saved
    :param name_prefix: Prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    """

    df.comp_1 = df.comp_1.map(lambda x: x.lstrip(name_prefix)).astype(int)
    df.comp_2 = df.comp_2.map(lambda x: x.lstrip(name_prefix)).astype(int)

    df.to_sql(table_name, con=engine, if_exists='append', index=False, method='multi', chunksize=10000)
