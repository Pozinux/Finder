import configparser
from mysql.connector import errorcode, Error, MySQLConnection
import os
import logging


class DatabaseGestion:
    def __init__(self):
        self.filename = os.getcwd() + '\\config_db.ini'
        self.section = 'mysql'
        self.dbc = {}
        self.conn = None
        self.cursor = None
        self.error_db_connection = None  # By default there is no connection error
        self.error_db_execution = None  # By default there is no connection error
        self.message_error_connection_db = None
        self.message_error_execution_db = None

    def __enter__(self):
        logging.debug("Database class def __enter__ context manager")
        logging.debug("Connection to the database.")
        self.read_db_config()
        try:
            self.conn = MySQLConnection(**self.dbc)
            self.cursor = self.conn.cursor(prepared=True)  # The search works with/without the prepared but not the update. WHY ?
        except Error as err:
            # Example of retrieved errors:
            # 1049 (42000): Base "Base_which_not_exists" unknown
            # 2003: Can't connect to MySQL server on 'localhost:3306' (10061 No connection could be established because the target computer expressly refused it)

            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:  # 1045
                self.error_db_connection = str(err)
                self.message_error_connection_db = self.error_db_connection + '\nCheck the account and password connection to the database.'
                print(self.message_error_connection_db)
            elif err.errno == errorcode.ER_BAD_DB_ERROR:  # 1049
                self.error_db_connection = str(err)
                self.message_error_connection_db = self.error_db_connection + '\nThe database does not exist.'
                print(self.message_error_connection_db)
            elif err.errno == 2003:  # 2003
                self.error_db_connection = str(err)
                self.message_error_connection_db = self.error_db_connection + '\nError connecting to the database. \nCheck that the database services are well launched, for example.'
                print(self.message_error_connection_db)
            else:
                self.error_db_connection = str(err)
                self.message_error_connection_db = self.error_db_connection + '\nError connecting to the database. Error number: ' + err.errno
                print(self.message_error_connection_db)
        return self  # We return the object otherwise in with there will be no object. With the use of with and the context manager, it is what __enter__ returns that is taken into account.

    def __exit__(self, *args):
        logging.debug("Database class def __exit__ context manager")
        if not self.error_db_connection:
            self.disconnect_db()

    def disconnect_db(self):
        self.cursor.close()
        self.conn.close()
        logging.debug("Database disconnect.")

    def sql_query_execute(self, sql):
        try:
            self.cursor.execute(sql)
        except Error as e:
            print(e)  # Exemple : 1146 (42S02): The table 'base_name.table_not_exists' does not exist
            print("Error query execute")

    def sql_query_executemany(self, sql, datalist):
        try:
            self.cursor.executemany(sql, datalist)
            self.conn.commit()
        except Error as err:
            if err.errno == 1054:  # 1054 (42S22): Field 'XXX' unknown in field list
                self.error_db_execution = str(err)
                self.message_error_execution_db = self.error_db_execution
                print(self.message_error_execution_db)
            elif err.errno == 1146:  # 1146 (42S02): The table 'base_name.table_not_exists' does not exist
                self.error_db_execution = str(err)
                self.message_error_execution_db = self.error_db_execution
                print(self.message_error_execution_db)
            else:
                self.error_db_execution = str(err)
                self.message_error_execution_db = self.error_db_execution
                print(self.message_error_execution_db)

    def rows(self):
        return self.cursor.rowcount

    def read_db_config(self):
        # Create a dictionary of database parameters
        # create parser and read ini configuration file
        parser = configparser.ConfigParser()
        parser.read(self.filename)
        # get section, default to mysql
        if parser.has_section(self.section):
            items = parser.items(self.section)
            for item in items:
                self.dbc[item[0]] = item[1]
        else: 
            raise Exception(f'Section {self.section} not found in the {self.filename} file. This error occures also when the script cannot find the file. Usualy because you run with clic-droit "Python"')
