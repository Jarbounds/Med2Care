###############################################################################
#                                                                             #  
# @author: Matilde Pato                                                       #  
# @email:  matilde.pato@gmail.com                                             #
# @date: 28 Jan 2020                                                          #
# @version: 1.0                                                               #  
# Lasige - FCUL                                                               #
#   (Adapted from Márcia Barros)                                              #  
# @last update:                                                               #  
#   version 1.1: 12 Feb 2021                                                  #      
#   (author: Matilde Pato, matilde.pato@gmail.com)                            #
#   version 1.2: 15 Feb 2023 add similarity columns: tanimoto & morgan        #      
#   (author: Matilde Pato, matilde.pato@gmail.com)                            #   
#                                                                             #  
###############################################################################

from sqlite3 import Error
import numpy as np
import pandas as pd

import mysql.connector as connector
from mysql.connector import MySQLConnection
from mysql.connector.cursor import MySQLCursor
from sqlalchemy import create_engine
from .myconfiguration import MyConfiguration as Config


def create_default_connection_mysql():
    """
    Create a default connection to the mysql database specified by host, user 
     and password defined in configurations.ini
    :param
    :return my_db: connection object
    """

    # assert isinstance( arg.password,object )
    config: Config = Config.get_instance()
    my_db = connector.connect(
        host=config.host,
        port=config.port,
        user=config.user,
        password=config.password,
        # ssl_disabled=True,
    )
    return my_db


def create_connection_mysql():
    """
    Create a connection to the mysql database specified by host, user, password and
    database name defined in configurations.ini
   :param
   :return my_db: connection object
   """
    my_db = create_default_connection_mysql()
    my_db.database = Config.get_instance().database
    return my_db


def create_engine_mysql():
    """
    Create a pool and dialect together connection to provide a source of database and behavior
    :param
    :return engine: connection engine object
    """

    # in case of connection error, change the host as in the next commented code
    config: Config = Config.get_instance()
    host = config.host
    port = config.port
    user = config.user
    passwd = config.password
    db_name = config.database

    engine = create_engine(
        "mysql+pymysql://{user}:{pw}@{host}:{port}/{db}"
        .format(
            user=user,
            pw=passwd,
            host=host,
            port=port,
            db=db_name
        ),
        pool_pre_ping=True
    )

    return engine


def check_database(database: str):
    """
    Check the existence of a database with the name defined in configurations.ini
     if none, a new is created as well as a table of similarity
    :param 
    :return none
    """

    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        my_db = create_default_connection_mysql()
        my_cursor = my_db.cursor()

        my_cursor.execute("show databases;")

        results = my_cursor.fetchall()
        results = [res[0] for res in results]

        if database in results:
            print("Database already exists")
        else:
            print("Will create database")
            my_cursor.execute(f"create database {database}")
    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


def check_table(database_name: str, table_name: str) -> bool:
    """
    Check the existence of table for a given database.
    :param database_name: database name
    :param table_name: Table name
    :return none
    """

    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        my_db = create_default_connection_mysql()
        my_cursor = my_db.cursor()

        query = f"show tables from {database_name};"
        my_cursor.execute(query)

        results = my_cursor.fetchall()
        results = [res[0] for res in results]

        if table_name in results:
            print(f'Table {table_name} already exists')
        else:
            print(f'Table {table_name} does not exist, creating')
            create_table(table_name)
    except Exception as e:
        print("Error while connecting to MySQL", e)
        return False
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


# ----------------------------------------------------------------------------------------------------- #

def create_table(table_name: str):
    """
    Create a table named similarity with in mysql which columns are
        <id, comp_1, comp_2, sim_resnik, sim_lin, sim_jc, sim_rel, sim_jac, sim_islch, 
        sim_tanimoto, sim_morgan> 
    :param: none
    :return:
    """

    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        my_db = create_connection_mysql()
        my_cursor = my_db.cursor()

        database = Config.get_instance().database

        my_cursor.execute(f'use {database}')

        my_cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        my_cursor.execute(
            f" CREATE TABLE `{table_name}` (`id` INT NOT NULL AUTO_INCREMENT,"
            "`comp_1` INT NOT NULL,"
            "`comp_2` INT NOT NULL, "
            "`sim_resnik` FLOAT NOT NULL, "
            "`sim_lin` FLOAT NOT NULL, "
            "`sim_jc` FLOAT NOT NULL, "
            "`sim_rel` FLOAT NOT NULL,"
            "`sim_jac` FLOAT NOT NULL,"
            "`sim_islch` FLOAT NOT NULL,"
            "`ts` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,"
            " PRIMARY KEY (`id`), "
            "INDEX sim (`comp_1`,`comp_2`) ) ENGINE = InnoDB")
        my_cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        my_db.commit()
        print(f"Table {table_name} created")
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


# ----------------------------------------------------------------------------------------------------- #

def add_columns(tablename):
    """

    Get the item 1, item 2 of the 1st quartile in the similarity db

    :param tablename: name of the table saved in mysql
    :param quart: quartile
    :return result: pandas DataFrame
    """
    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None

    try:
        # Open database connection
        my_db = create_connection_mysql()

        # prepare a cursor object using cursor() method
        my_cursor = mydb.cursor()

        # Prepare SQL query to read a record into the database.        
        sql = f"ALTER TABLE {tablename} \
                    ADD COLUMN sim_resnick` FLOAT NOT NULL AFTER sim_lin, \
                    ADD COLUMN sim_jc` FLOAT NOT NULL AFTER sim_lin \
                "
        my_cursor.execute(sql)

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_db is not None and my_db.is_connected():
            if my_cursor is not None:
                my_cursor.close()
            my_db.close()


# ----------------------------------------------------------------------------------------------------- #

def create_norm_table(tablename, sim):
    """
    
    Create a table named norm_similarity with in mysql which columns are
        <id, comp_1, comp_2, similarity, l2, zscore, min-max, tanh, logistic sig> 
    :param: none
    :return:
    """
    global mydb
    try:
        mydb = create_connection_mysql()

        mycursor = mydb.cursor()

        mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        mycursor.execute(f"DROP TABLE IF EXISTS `{tablename}`")

        mycursor.execute(
            f" CREATE TABLE `{tablename}` (`id` INT NOT NULL AUTO_INCREMENT, \
            `comp_1` INT NOT NULL, \
            `comp_2` INT NOT NULL, \
            `{sim}` FLOAT NOT NULL, \
            `l2` FLOAT NOT NULL, \
            `zscore` FLOAT NOT NULL, \
            `min-max` FLOAT NOT NULL,\
            `tanh` FLOAT NOT NULL,\
            `log-sig` FLOAT NOT NULL,\
             PRIMARY KEY (`id`), \
             INDEX sim (`comp_1`,`comp_2`) ) ENGINE = InnoDB")
        mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print(f"Table {tablename} already exists")
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()


# ----------------------------------------------------------------------------------------------------- #

def create_structuraltable(tablename):
    """
    Create a table named similarity with in mysql which columns are
        <id, comp_1, comp_2, sim_tanimoto, sim_morgan> 
    :param: none
    :return:
    """
    global mydb
    try:
        mydb = create_connection_mysql()

        mycursor = mydb.cursor()

        mycursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        mycursor.execute(f"DROP TABLE IF EXISTS `{tablename}`")

        mycursor.execute(
            f" CREATE TABLE `{tablename}` (`id` INT NOT NULL AUTO_INCREMENT,"
            "`comp_1` INT NOT NULL,"
            "`comp_2` INT NOT NULL, "
            "`sim_tanimoto` FLOAT NULL, "
            "`sim_morgan` FLOAT NULL, "
            " PRIMARY KEY (`id`), "
            "INDEX sim (`comp_1`,`comp_2`) ) ENGINE = InnoDB")
        mycursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print(f"Table {tablename} already exists")
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()


# ----------------------------------------------------------------------------------------------------- #

def get_column(tablename, column='sim_resnik'):
    """

    Get the item 1, item 2, and column in the similarity db

    :param tablename: name of the table saved in mysql
    :param column: column
    :return result: pandas DataFrame
    """
    global mydb, result
    try:
        # Open database connection
        mydb = create_connection_mysql()

        # prepare a cursor object using cursor() method
        mycursor = mydb.cursor()

        # Prepare SQL query to read a record into the database.        
        sql = f"SELECT comp_1, comp_2, {column} FROM {tablename};"
        mycursor.execute(sql)

        result = mycursor.fetchall()

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

    return result


# ----------------------------------------------------------------------------------------------------- #

# def create_table(tablename):
#     """

#     Create a table named similarity with in mysql which columns are
#         <id, comp_1, comp_2, sim_resnik, sim_lin, sim_jc, geom_mean, range, std> 
#     :param: none
#     :return:
#     """
#     global mydb
#     try:
#         mydb = create_connection_mysql()

#         mycursor = mydb.cursor()

#         mycursor.execute( "SET FOREIGN_KEY_CHECKS = 0" )
#         mycursor.execute( f"DROP TABLE IF EXISTS `{tablename}`" )

#         mycursor.execute(
#             f" CREATE TABLE `{tablename}` (`id` INT NOT NULL AUTO_INCREMENT,"
#             "`comp_1` INT NOT NULL,"  
#             "`comp_2` INT NOT NULL, "
#             "`sim_resnik` FLOAT NOT NULL, "
#             "`sim_lin` FLOAT NOT NULL, "
#             "`sim_jc` FLOAT NOT NULL,"
#             "`geom_mean` FLOAT NOT NULL, "
#             "`span` FLOAT NOT NULL, "
#             "`std` FLOAT NOT NULL,"
#             " PRIMARY KEY (`id`), "
#             "INDEX sim (`comp_1`,`comp_2`) ) ENGINE = InnoDB" )

#         mycursor.execute( "SET FOREIGN_KEY_CHECKS = 1" )
#         print( "Table already exists" )
#     except Error as e:
#         print( "Error while connecting to MySQL", e )
#     finally:
#         if mydb.is_connected():
#             mycursor.close()
#             mydb.close()   
# # ----------------------------------------------------------------------------------------------------- #

# def get_items_ids(dataset, name_prefix):
#     """

#     Get the ids of each items in the dataset
#     :param dataset: cvs dataset
#     :param name_prefix: Prefix of the concepts to be extracted from the ontology
#     :type name_prefix: string
#     :return ids: ids of each row of the dataset
#     """

#     if ( dataset.dtypes['item'] == np.object ):
#         dataset.item = dataset.item.map( lambda x: x.lstrip( name_prefix ) ).astype('int64')
#     return dataset.item.unique()

# # ----------------------------------------------------------------------------------------------------- #

# def confirm_all_test_train_similarities(entry_ids_1, entry_ids_2, pairs_from_db):
#     """

#     Checks if all item-item pair was found in the database
#      for each entry_ids_1 and entry_ids_2
#     Important: the values must be in string format because of HPO 
#     :param entry_ids_1: list of entries 1
#     :param entry_ids_2: list of entries 2
#     :return: list with results not found combinations pandas Dataframe

#     """
#     lists_combinations = pd.DataFrame( list( product( entry_ids_1, entry_ids_2 ) ),
#                                        columns=['l1', 'l2'] )

#     ss = lists_combinations.l1.isin( pairs_from_db.comp_1.astype( 'int64' ).tolist() ) \
#         & lists_combinations.l2.isin( pairs_from_db.comp_2.astype( 'int64' ).tolist() ) 

#     ss2 = lists_combinations.l2.isin( pairs_from_db.comp_1.astype( 'int64' ).tolist() ) \
#         & lists_combinations.l1.isin( pairs_from_db.comp_2.astype( 'int64' ).tolist() )

#     not_found_in_db = lists_combinations[ (~ss) & (~ss2) ]

#     not_found_list_1 = not_found_in_db.l1.unique().tolist()
#     not_found_list_2 = not_found_in_db.l2.unique().tolist()

#     return not_found_list_1, not_found_list_2

# ----------------------------------------------------------------------------------------------------- #

def get_similar(tablename, quart, sim):
    """

    Get the item 1, item 2 of the 1st quartile in the similarity db

    :param tablename: name of the table saved in mysql
    :param quart: quartile
    :param sim: similarity metric
    :return result: pandas DataFrame
    """
    global mydb, result
    try:
        # Open database connection
        mydb = create_connection_mysql()

        # prepare a cursor object using cursor() method
        mycursor = mydb.cursor()

        # Prepare SQL query to read a record into the database.        
        sql = f"SELECT comp_1, comp_2 FROM {tablename} where {sim} >= ( \
                    SELECT {sim} \
                    FROM ( SELECT s.*,  @row_num :=@row_num + 1 AS row_num \
                            FROM {tablename} s, (SELECT @row_num:=0) counter \
                            ORDER BY {sim} DESC ) temp \
                    WHERE temp.row_num = ROUND({quart}* @row_num) \
                ) "
        mycursor.execute(sql)

        result = mycursor.fetchall()

        if len(result) != 0:
            result = pd.DataFrame(np.array(result), columns=['comp_1', 'comp_2'])

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

    return result


# ----------------------------------------------------------------------------------------------------- #

def save_to_mysql(df, table_name, name_prefix=None):
    """
    :param df: pandas DataFrame
    :param engine: connection to engine object
    :param table_name: name of the table where the data are saved
    :param name_prefix: Prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    """
    con = None
    try:

        # engine = create_engine_mysql()
        # conn = engine.connect()
        # mydb = connector.connect(
        #     host=cfg.getInstance().host,
        #     user=cfg.getInstance().user,
        #     password=cfg.getInstance().password,
        #     db = cfg.getInstance().database
        # )
        config: Config = Config.get_instance()
        host = config.host
        user = config.user
        port = config.port
        passwd = config.password
        db_name = config.database

        engine = create_engine("mysql+pymysql://{user}:{pw}@{host}:{port}/{db}"
                               .format(user=user,
                                       pw=passwd,
                                       host=host,
                                       port=port,
                                       db=db_name),
                               pool_pre_ping=True)

        con = engine.connect()

        # save to db with string type instead of int
        if name_prefix:
            df.comp_1 = df.comp_1.map(lambda x: x.lstrip(name_prefix)).astype(int)
            df.comp_2 = df.comp_2.map(lambda x: x.lstrip(name_prefix)).astype(int)

        df.to_sql(name=table_name, con=con, if_exists='append', index=False, method='multi', chunksize=10000)
        print('end save values')
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if con is not None:
            con.commit()
            con.close()


# ----------------------------------------------------------------------------------------------------- #

def get_dbvalues(tablename, id=None, limit=None):
    """

    Get the item 1, item 2 and similarity in the similarity db

    :param tablename: name of the table saved in mysql
    :param sim: similarity metric
    :return result: pandas DataFrame
    """
    global mydb, result
    try:
        # Open database connection
        mydb = create_connection_mysql()

        # prepare a cursor object using cursor() method
        mycursor = mydb.cursor()

        # Prepare SQL query to read a record into the database.  
        if id and limit:
            sql = f"SELECT * FROM {tablename} where id > {id} limit {limit}"  # 225271|226|227|228|237434
        else:
            sql = f"SELECT * FROM {tablename} where id > 224271 limit 1000"  # 225271|226|227|228|237434
        # sql = f"SELECT comp_1, comp_2, {sim} FROM {tablename}"
        mycursor.execute(sql)
        result = mycursor.fetchall()

        if len(result) != 0:
            # result = pd.DataFrame( np.array(result), columns=['comp_1', 'comp_2',{sim}] )
            result = pd.DataFrame(np.array(result)[:, 1:3], columns=['comp_1', 'comp_2'])

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

    return result


# ----------------------------------------------------------------------------------------------------- #

def get_minmax(tablename):
    """

    Get the minimum and maximum id in a table

    :param tablename: name of the table saved in mysql
    :return result: dictionary with minimum and maximum of id in msql table
    """
    global mydb, result
    try:
        # Open database connection
        mydb = create_connection_mysql()

        # prepare a cursor object using cursor() method
        mycursor = mydb.cursor()

        # Prepare SQL query to read a record into the database.        
        sql = f"SELECT min(id), max(id) FROM {tablename}"
        mycursor.execute(sql)

        result = mycursor.fetchall()
        if len(result) != 0:
            result = dict({'min': [item[0] for item in result][0], 'max': [item[1] for item in result][0]})

    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

    return result


# ----------------------------------------------------------------------------------------------------- #

def drop_duplicates(tablename):
    """
    Drop duplicates from table
    :param tablename: name of the table saved in mysql
    """
    global mydb
    try:
        # Open database connection
        mydb = create_connection_mysql()
        # prepare a cursor object using cursor() method
        mycursor = mydb.cursor()

        # Prepare SQL query to read a record into the database.        
        sql = f"delete t1 from {tablename} t1 inner join {tablename} t2 \
            where t1.id < t2.id and t1.comp_1 = t2.comp_1 and t1.comp_2 = t2.comp_2;"
        mycursor.execute(sql)
        print(f"Duplicated from {tablename} were removed")
    except Error as e:
        print("Error while connecting to MySQL", e)
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
