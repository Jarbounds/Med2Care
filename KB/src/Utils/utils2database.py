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

#import sqlite3
from itertools import product
from pickle import TRUE
from sqlite3 import Error
import numpy as np
import pandas as pd

import mysql.connector as connector
from sqlalchemy import create_engine
from myconfiguration import MyConfiguration as cfg
import pymysql

# ----------------------------------------------------------------------------------------------------- #

def create_default_connection_mysql():
    """

    Create a default connection to the mysql database specified by host, user 
     and password defined in config.ini
    :param
    :return mydb: connection object
    """
    
    #assert isinstance( arg.password,object )
    mydb = connector.connect(
        host=cfg.getInstance().host,
        user=cfg.getInstance().user,
        password=cfg.getInstance().password
    )
    return mydb

# ----------------------------------------------------------------------------------------------------- #

def create_connection_mysql():
    """
   
   Create a connection to the mysql database specified by host, user, password and
    database name defined in config.ini
   :param
   :return mydb: connection object
   """
    mydb = create_default_connection_mysql()
    mydb.database = cfg.getInstance().database
    return mydb

# # ----------------------------------------------------------------------------------------------------- #

# def create_connection_sqlite(sb_file):
#     """ 
    
#     Create a database connection to the SQLite database specified by sb_file
#     :param sb_file: File name of database where semantic base will be stored
#     :type sb_file: string
#     :return conn: connection object or none
#     """
#     try:
#         conn = sqlite3.connect( sb_file )
#         return conn
#     except Error as e:
#         print( e )

#     return None

# ----------------------------------------------------------------------------------------------------- #

def create_engine_mysql():
    """
    
    Create a pool and dialect together connection to provide a source of database and behavior
    :param
    :return engine: connection engine object
    """
    
    # in case of connection error, change the host as in the next commented code

    host=cfg.getInstance().host,
    user=cfg.getInstance().user,
    passwd=cfg.getInstance().password
    db_name = cfg.getInstance().database

    engine = create_engine( "mysql+pymysql://{user}:{pw}@{host}/{db}"
                            .format( user=user,
                                     pw=passwd,
                                     host=host,
                                     db=db_name ),
                            pool_pre_ping=True )

    return engine

# ----------------------------------------------------------------------------------------------------- #

def check_database():
    """
    Check the existence of a database with the name defined in config.ini 
     if none, a new is created as well as a table of similarity
    :param 
    :return none
    """
    
    global mydb
    try:
        check = False
        mydb = create_default_connection_mysql()
        mycursor = mydb.cursor()
        db_name = cfg.getInstance().database

        mycursor.execute( "SHOW DATABASES" )
        for x in mycursor:

            if x[0].decode( "unicode-escape" ) == db_name:  #scratchy
            # or,
            # if x[0].encode().decode( 'utf-8' ) == db_name: #chronos
                check = True

        if not check:
            print( "Will create database" )
            mycursor.execute( "CREATE DATABASE " + db_name )
            #create_table(tablename)
        else:
            print( "Database already exists" )

    except Error as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

# ----------------------------------------------------------------------------------------------------- #

def check_structural_chebi(tablename):
    """
    Check the existence of a database with the name defined in config.ini 
     if none, a new is created as well as a table of similarity
    :param 
    :return none
    """
    
    global mydb
    try:
        mydb = create_default_connection_mysql()
        mycursor = mydb.cursor()
        db_name = cfg.getInstance().database
        stmt = f"SHOW TABLES FROM {db_name}"
        mycursor.execute(stmt)
        for x in mycursor:

            if x[0].decode( "unicode-escape" ) == tablename:  #scratchy
                mycursor.close()
                mydb.close()
                return TRUE

    except Error as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
    return False

# ----------------------------------------------------------------------------------------------------- #

def create_table(tablename):
    """
    
    Create a table named similarity with in mysql which columns are
        <id, comp_1, comp_2, sim_resnik, sim_lin, sim_jc, sim_rel, sim_jac, sim_islch, 
        sim_tanimoto, sim_morgan> 
    :param: none
    :return:
    """
    global mydb
    try:
        mydb = create_connection_mysql()

        mycursor = mydb.cursor()

        mycursor.execute( "SET FOREIGN_KEY_CHECKS = 0" )
        mycursor.execute( f"DROP TABLE IF EXISTS `{tablename}`" )

        mycursor.execute(
            f" CREATE TABLE `{tablename}` (`id` INT NOT NULL AUTO_INCREMENT,"
            "`comp_1` INT NOT NULL,"  
            "`comp_2` INT NOT NULL, "
            "`sim_resnik` FLOAT NOT NULL, "
            "`sim_lin` FLOAT NOT NULL, "
            "`sim_jc` FLOAT NOT NULL, "
            "`sim_rel` FLOAT NOT NULL,"
            "`sim_jac` FLOAT NOT NULL,"
            "`sim_islch` FLOAT NOT NULL,"
            " PRIMARY KEY (`id`), "
            "INDEX sim (`comp_1`,`comp_2`) ) ENGINE = InnoDB" )
        mycursor.execute( "SET FOREIGN_KEY_CHECKS = 1" )
        print( f"Table {tablename} already exists" )
    except Error as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

# ----------------------------------------------------------------------------------------------------- #

def add_columns(tablename):
    """

    Get the item 1, item 2 of the 1st quartile in the similarity db

    :param tablename: name of the table saved in mysql
    :param quart: quartile
    :return result: pandas DataFrame
    """
    global mydb
    try:
        # Open database connection
        mydb = create_connection_mysql()

        # prepare a cursor object using cursor() method
        mycursor = mydb.cursor()
        
        # Prepare SQL query to read a record into the database.        
        sql = f"ALTER TABLE {tablename} \
                    ADD COLUMN sim_resnick` FLOAT NOT NULL AFTER sim_lin, \
                    ADD COLUMN sim_jc` FLOAT NOT NULL AFTER sim_lin \
                "
        mycursor.execute( sql )
       
    except Error as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()

# ----------------------------------------------------------------------------------------------------- #

def create_norm_table(tablename,sim):
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

        mycursor.execute( "SET FOREIGN_KEY_CHECKS = 0" )
        mycursor.execute( f"DROP TABLE IF EXISTS `{tablename}`" )
        
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
             INDEX sim (`comp_1`,`comp_2`) ) ENGINE = InnoDB" )
        mycursor.execute( "SET FOREIGN_KEY_CHECKS = 1" )
        print( f"Table {tablename} already exists" )
    except Error as e:
        print( "Error while connecting to MySQL", e )
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

        mycursor.execute( "SET FOREIGN_KEY_CHECKS = 0" )
        mycursor.execute( f"DROP TABLE IF EXISTS `{tablename}`" )

        mycursor.execute(
            f" CREATE TABLE `{tablename}` (`id` INT NOT NULL AUTO_INCREMENT,"
            "`comp_1` INT NOT NULL,"  
            "`comp_2` INT NOT NULL, "
            "`sim_tanimoto` FLOAT NULL, "
            "`sim_morgan` FLOAT NULL, "
            " PRIMARY KEY (`id`), "
            "INDEX sim (`comp_1`,`comp_2`) ) ENGINE = InnoDB" )
        mycursor.execute( "SET FOREIGN_KEY_CHECKS = 1" )
        print( f"Table {tablename} already exists" )
    except Error as e:
        print( "Error while connecting to MySQL", e )
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
        mycursor.execute( sql )
       
        result = mycursor.fetchall()
                
    except Error as e:
        print( "Error while connecting to MySQL", e )
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
        mycursor.execute( sql )
       
        result = mycursor.fetchall()

        if len( result ) != 0:
            result = pd.DataFrame( np.array( result ), columns=['comp_1', 'comp_2'] )

    except Error as e:
        print( "Error while connecting to MySQL", e )
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
    #global mydb
    try: 
        
        # engine = create_engine_mysql()
        # conn = engine.connect()
        # mydb = connector.connect(
        #     host=cfg.getInstance().host,
        #     user=cfg.getInstance().user,
        #     password=cfg.getInstance().password,
        #     db = cfg.getInstance().database
        # )
        host=cfg.getInstance().host
        user=cfg.getInstance().user
        passwd=cfg.getInstance().password
        db_name = cfg.getInstance().database
        
        engine = create_engine( "mysql+pymysql://{user}:{pw}@{host}/{db}"
                                .format( user=user,
                                            pw=passwd,
                                            host=host,
                                            db=db_name ),
                                pool_pre_ping=True )

        con = engine.connect()
        
        # save to db with string type instead of int
        if name_prefix:
            df.comp_1 = df.comp_1.map( lambda x: x.lstrip( name_prefix ) ).astype(int)
            df.comp_2 = df.comp_2.map( lambda x: x.lstrip( name_prefix ) ).astype(int)
       
        """if name_prefix != 'HP_':
        df.comp_1 = df.comp_1.astype( int )
        df.comp_2 = df.comp_2.astype( int )
        """
        
        df.to_sql(name=table_name, con=con, if_exists='append', index=False, method='multi', chunksize=10000)
        print('end save values')
    except Error as e:
        print( "Error while connecting to MySQL", e )


# ----------------------------------------------------------------------------------------------------- #

def get_values(tablename, sim):
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
        sql = f"SELECT comp_1, comp_2, {sim} FROM {tablename}"
        mycursor.execute( sql )
       
        result = mycursor.fetchall()

        if len( result ) != 0:
            result = pd.DataFrame( np.array( result ), columns=['comp_1', 'comp_2',f"{sim}"] )

    except Error as e:
        print( "Error while connecting to MySQL", e )
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
        mycursor.execute( sql )
        print( f"Duplicated from {tablename} were removed" )
    except Error as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()
