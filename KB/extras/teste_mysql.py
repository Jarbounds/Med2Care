from sqlalchemy import create_engine
import pandas as pd

from itertools import product
from sqlite3 import Error
import numpy as np
import pandas as pd


import mysql.connector as connector
from sqlalchemy import create_engine
import pymysql

# ----------------------------------------------------------------------------------------------------- #

def create_default_connection_mysql():
    """

    Create a default connection to the mysql database specified by host, user 
     and password defined in configurations.ini
    :param
    :return mydb: connection object
    """

    #assert isinstance( arg.password,object )

    mydb = connector.connect(
        host='172.17.0.13', #mpato@10.10.0.24
        user='root',
        password='1234'
    )
    return mydb

# ----------------------------------------------------------------------------------------------------- #

def create_connection_mysql():
    """
   
   Create a connection to the mysql database specified by host, user, password and
    database name defined in configurations.ini
   :param
   :return mydb: connection object
   """
    mydb = create_default_connection_mysql()
    mydb.database = 'entities_sim_cord19_rs'

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
    host='172.17.0.13', 
    user='root',
    passwd='1234'
    db_name = 'entities_sim_cord19_rs'

    engine = create_engine( "mysql+pymysql://{user}:{pw}@{host}/{db}"
                            .format( user=user,
                                     pw=passwd,
                                     host=host,
                                     db=db_name ),
                            pool_pre_ping=True )

    return engine

def check_database():
    """
    Check the existence of a database with the name defined in configurations.ini
     if none, a new is created as well as a table of similarity
    :param 
    :return none
    """

    global mydb
    try:
        check = False
        mydb = create_default_connection_mysql()
        mycursor = mydb.cursor()
        db_name = 'entities_sim_cord19_rs'

        mycursor.execute( "SHOW DATABASES" )
        for x in mycursor:

            if x[0].decode( "unicode-escape" ) == db_name:
            # or,
            #if x[0].encode().decode( 'utf-8' ) == db_name: #chronos
                check = True

        if not check:
            print( "Will create database" )
            mycursor.execute( "CREATE DATABASE " + db_name )
            
        else:
            print( "Database already exists" )

    except Error as e:
        print( "Error while connecting to MySQL", e )
    finally:
        if mydb.is_connected():
            mycursor.close()
            mydb.close()


def get_results(tablename):
    """

    Get the item 1, item 2 of the 1st quartile in the similarity db

    :param tablename: name of the table saved in mysql
    :return result: pandas DataFrame
    """
    global mydb, result
    try:
        # Open database connection
        mydb = create_connection_mysql()

        # prepare a cursor object using cursor() method
        mycursor = mydb.cursor()
        
        # Prepare SQL query to read a record into the database.        
        sql = f"SELECT * FROM {tablename} "
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


check_database()
# in case of connection error, change the host as in the next commented code
host='172.17.0.13' #mpato@10.10.0.24
user='root'
password='1234'
db_name='entities_sim_cord19_rs'

engine = create_engine( "mysql+pymysql://{user}:{pw}@{host}/{db}"
                        .format( user=user,
                                    pw=password,
                                    host=host,
                                    db=db_name ),
                        pool_pre_ping=True )

con = engine.connect()
df = pd.DataFrame(['A','B'],columns=['new_tablecol'])
df.to_sql(name='new_table',con=con,if_exists='append')

result= get_results(tablename='new_table')
print(result)

con.close()