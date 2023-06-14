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
import time

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

    config: Config = Config.get_instance()

    host = config.host
    port = config.port
    user = config.user
    password = config.password

    my_db = connector.connect(
        host=host,
        port=port,
        user=user,
        password=password,
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
    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


def create_norm_table(table_name: str, sim: str):
    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        my_db = create_connection_mysql()
        my_cursor = my_db.cursor()

        database = Config.get_instance().database

        my_cursor.execute(f'use {database};')

        my_cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        my_cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

        my_cursor.execute(
            f" CREATE TABLE `{table_name}` (`id` INT NOT NULL AUTO_INCREMENT, \
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
        my_cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print(f"Table {table_name} created")
    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


def add_columns(table_name):
    """
    Get the item 1, item 2 of the 1st quartile in the similarity db

    :param table_name: name of the table saved in mysql
    :return result: pandas DataFrame
    """

    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        # Open database connection
        my_db = create_connection_mysql()

        # prepare a cursor object using cursor() method
        my_cursor = my_db.cursor()

        # Prepare SQL query to read a record into the database.        
        sql = f"ALTER TABLE {table_name} \
                    ADD COLUMN sim_resnick` FLOAT NOT NULL AFTER sim_lin, \
                    ADD COLUMN sim_jc` FLOAT NOT NULL AFTER sim_lin \
                "
        my_cursor.execute(sql)

    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


def check_norm_table(table_name: str, sim: str):
    """
    Create a table named norm_similarity with in mysql which columns are 
    <id, comp_1, comp_2, similarity, l2, zscore, min-max, tanh, logistic sig> 
    :param: none
    :return:
    """

    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        my_db = create_default_connection_mysql()
        my_cursor = my_db.cursor()

        database: str = Config.get_instance().database

        query = f"show tables from {database};"
        my_cursor.execute(query)

        results = my_cursor.fetchall()
        results = [res[0] for res in results]

        if table_name in results:
            print(f'Table {table_name} already exists')
            return

        print(f'Table {table_name} does not exist, creating')
        create_norm_table(table_name, sim)
    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


def create_structural_table(table_name):
    """
    Create a table named similarity with in mysql which columns are <id, comp_1, comp_2, sim_tanimoto, sim_morgan> 
    :param: none
    :return:
    """

    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        my_db = create_connection_mysql()

        my_cursor = my_db.cursor()

        my_cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        my_cursor.execute(f"DROP TABLE IF EXISTS `{table_name}`")

        my_cursor.execute(
            f" CREATE TABLE `{table_name}` "
            f"(`id` INT NOT NULL AUTO_INCREMENT,"
            "`comp_1` INT NOT NULL,"
            "`comp_2` INT NOT NULL, "
            "`sim_tanimoto` FLOAT NULL, "
            "`sim_morgan` FLOAT NULL, "
            " PRIMARY KEY (`id`), "
            "INDEX sim (`comp_1`,`comp_2`) ) ENGINE = InnoDB")
        my_cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        print(f"Table {table_name} already exists")
    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


def get_column(table_name, column='sim_resnik'):
    """
    Get the item 1, item 2, and column in the similarity db

    :param table_name: name of the table saved in mysql
    :param column: column
    :return result: pandas DataFrame
    """
    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        # Open database connection
        my_db = create_connection_mysql()

        # prepare a cursor object using cursor() method
        my_cursor = my_db.cursor()

        # Prepare SQL query to read a record into the database.        
        sql = f"SELECT comp_1, comp_2, {column} FROM {table_name};"
        my_cursor.execute(sql)

        result = my_cursor.fetchall()
        return result
    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_db.is_connected():
            my_cursor.close()
            my_db.close()


def get_similar(table_name, quart, metric):
    """
    Get the item 1, item 2 of the 1st quartile in the similarity db
    :param table_name: name of the table saved in mysql
    :param quart: quartile
    :param metric: similarity metric
    :return result: pandas DataFrame
    """
    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        # Open database connection
        my_db = create_connection_mysql()

        # prepare a cursor object using cursor() method
        my_cursor = my_db.cursor()

        database: str = Config.get_instance().database

        my_cursor.execute(f'use {database};')

        sql = f"select comp_1, comp_2 " \
              f"from (" \
              f"select comp_1, comp_2, {metric}, " \
              f"row_number() over (order by {metric} desc) as row_num," \
              f"count(*) over () as total_rows " \
              f"from {table_name}" \
              f") temp " \
              f"where row_num <= ceil({quart} * total_rows)"
        my_cursor.execute(sql)
        all_results = my_cursor.fetchall()
        if len(all_results) != 0:
            return pd.DataFrame(np.array(all_results), columns=['comp_1', 'comp_2'])
    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


def save_to_mysql(df, table_name, name_prefix=None):
    """
    :param df: pandas DataFrame
    :param table_name: name of the table where the data are saved
    :param name_prefix: Prefix of the concepts to be extracted from the ontology
    :type name_prefix: string
    """
    con = None
    try:
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
    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if con is not None:
            con.commit()
            con.close()


def get_db_values(table_name, id=None, limit=None):
    """
    Get the item 1, item 2 and similarity in the similarity db

    :param table_name: name of the table saved in mysql
    :param sim: similarity metric
    :return result: pandas DataFrame
    """

    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        # Open database connection
        my_db = create_connection_mysql()

        # prepare a cursor object using cursor() method
        my_cursor = my_db.cursor()

        # Prepare SQL query to read a record into the database.  
        if id and limit:
            sql = f"SELECT * FROM {table_name} where id > {id} limit {limit}"  # 225271|226|227|228|237434
        else:
            sql = f"SELECT * FROM {table_name} where id > 224271 limit 1000"  # 225271|226|227|228|237434
        # sql = f"SELECT comp_1, comp_2, {sim} FROM {tablename}"
        my_cursor.execute(sql)
        result = my_cursor.fetchall()

        if len(result) != 0:
            # result = pd.DataFrame( np.array(result), columns=['comp_1', 'comp_2',{sim}] )
            return pd.DataFrame(np.array(result)[:, 1:3], columns=['comp_1', 'comp_2'])

    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


def dump_database(database_name: str, table_name: str, columns: str):
    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        my_db = create_connection_mysql()
        my_cursor = my_db.cursor()

        query = f'use {database_name};'
        my_cursor.execute(query)

        query = f'select {columns} from {table_name}'
        my_cursor.execute(query)

        with open(f'../data/{table_name}_{time.time_ns()}.sql', 'w') as fp:
            while True:
                row_set = my_cursor.fetchmany(10)
                if len(row_set) == 0:
                    break
                insert_query = \
                    f'insert into {database_name}.{table_name} ({columns}) values '
                values_str = ''
                for row in row_set:
                    instance = '('
                    for field in row:
                        instance += f'{field},'
                    instance = instance[:-1] + '),'
                    values_str += instance
                insert_query += values_str[:-1] + ';' + '\n'
                fp.write(insert_query)
    except Exception as e:
        print('Exception occurred in table dump, printing exception... ', e, sep='\n')
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


def get_minmax(table_name):
    """
    Get the minimum and maximum id in a table

    :param table_name: name of the table saved in mysql
    :return result: dictionary with minimum and maximum of id in msql table
    """

    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        # Open database connection
        my_db = create_connection_mysql()

        # prepare a cursor object using cursor() method
        my_cursor = my_db.cursor()

        # Prepare SQL query to read a record into the database.        
        sql = f"SELECT min(id), max(id) FROM {table_name}"
        my_cursor.execute(sql)

        result = my_cursor.fetchall()
        if len(result) != 0:
            return dict({'min': [item[0] for item in result][0], 'max': [item[1] for item in result][0]})

    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()


def drop_duplicates(table_name):
    """
    Drop duplicates from table
    :param table_name: name of the table saved in mysql
    """

    my_db: MySQLConnection | None = None
    my_cursor: MySQLCursor | None = None
    try:
        # Open database connection
        my_db = create_connection_mysql()
        # prepare a cursor object using cursor() method
        my_cursor = my_db.cursor()

        # Prepare SQL query to read a record into the database.        
        sql = f"delete t1 from {table_name} t1 inner join {table_name} t2 \
            where t1.id < t2.id and t1.comp_1 = t2.comp_1 and t1.comp_2 = t2.comp_2;"
        my_cursor.execute(sql)
        print(f"Duplicated from {table_name} were removed")
    except Exception as e:
        print("Error while connecting to MySQL", e)
    finally:
        if my_cursor is not None:
            my_cursor.close()
        if my_db is not None and my_db.is_connected():
            my_db.close()
