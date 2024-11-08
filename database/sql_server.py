# database/sql_server.py

import pyodbc
from config import SQL_SERVER_CONFIG

class SQLServerConnection:
    def __init__(self):
        self.connection = None

    def connect(self):
        for driver in SQL_SERVER_CONFIG['drivers']:
            conn_str = (
                f"Driver={{{driver}}};"
                f"Server={SQL_SERVER_CONFIG['server']};"
                f"Database={SQL_SERVER_CONFIG['database']};"
                f"UID={SQL_SERVER_CONFIG['username']};"
                f"PWD={SQL_SERVER_CONFIG['password']};"
                "Encrypt=yes;TrustServerCertificate=yes;"
            )
            try:
                self.connection = pyodbc.connect(conn_str)
                print(f"Connected to SQL Server using driver: {driver}")
                return
            except pyodbc.InterfaceError as e:
                print(f"Failed to connect using driver {driver}: {e}")
        raise Exception("Failed to connect with all provided ODBC drivers.")

    def fetch_data(self, query, params=None):
        cursor = self.connection.cursor()
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        return cursor.fetchall()

    def close(self):
        if self.connection:
            self.connection.close()
