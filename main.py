# main.py

# pip install sshtunnel
# pip install requests

import requests
import json
import os
from config import API_CONFIG
from database.sql_server import SQLServerConnection
from database.data_processor import DataProcessor
from logger import Logger

TIMESTAMP_FILE = 'timestamps.json'

class App:
    def __init__(self):
        # Initialize database connections, data processor and logger
        self.sql_server = SQLServerConnection()
        self.data_processor = DataProcessor()
        self.logger = Logger()

    def sync_orders(self):

        SQL_QUERY = """
            SELECT Belegdatum AS Datum, Belegnummer AS Auftragsnr, A0Empfaenger AS Kdnr, 
                A0Matchcode AS Kunde, USER_UnserZeichen AS UnserZeichen, Vertreter, USER_Kennung 
                AS Kennung, Nettobetrag AS GesamtNetto, Rabattbetrag1 as Porto, Timestamp
            FROM [OLReweAbf].[dbo].[KHKVKBelege] 
            WHERE Belegart = 'Auftragsbestätigung'
                AND Timestamp > ?
            """

        rows = self.fetch_SQL_data(SQL_QUERY, "orders")
        if not rows or len(rows) == 0:
            self.logger.write_log("Keine neuen Bestellungen gefunden!")
            print("No new data found!")
            return
        
        print("Data fetched from SQL Server.")

        # Process each row and collect it in a list
        data_list = [self.data_processor.process_order_row(row) for row in rows]

        # add the query_type
        payload = {
            "query_type": "sync_orders",
            "data": data_list
        }

        # Send all data in one request to the API
        response = self.send_to_api(payload)
        if not response:
            self.logger.write_log("sync_orders Methode hat keine json response erhalten!")
            return
        
        # write response into log file
        self.logger.process_response(response)

    def fetch_SQL_data(self, query, mode):
        rows = None
        # get latest timestamp for query
        timestamp_hex = self.get_timestamp(mode)
        timestamp_bytes = bytearray.fromhex(timestamp_hex) if timestamp_hex else None

        # fetches data from the MS SQL Server
        try:
            # Connect to SQL Server and fetch data
            self.sql_server.connect()
            if timestamp_bytes:
                rows = self.sql_server.fetch_data(query, (timestamp_bytes,))
            else:
                # Remove the `AND Timestamp > ?` condition if last_timestamp_bytes is None
                rows = self.sql_server.fetch_data(query.replace("AND Timestamp > ?", ""))

            if not rows or len(rows) == 0:
                return

            # save new latest timestamp
            latest_timestamp = max(row.Timestamp.hex() for row in rows)
            if latest_timestamp:
                self.save_timestamp(latest_timestamp, mode)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            self.sql_server.close()
            return rows

    def send_to_api(self, payload):
        # Send the entire data list as JSON payload in one request
        try:
            response = requests.post(API_CONFIG['url'], json=payload, headers=API_CONFIG['headers'])
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")
            return

    def get_timestamp(self, mode):
        if os.path.exists(TIMESTAMP_FILE):
            with open(TIMESTAMP_FILE, 'r') as file:
                data = json.load(file)
                return data.get(mode)
        return None

    def save_timestamp(self, timestamp, mode):
        if os.path.exists(TIMESTAMP_FILE):
            with open(TIMESTAMP_FILE, 'r') as file:
                data = json.load(file)
        else:
            data = {}

        # Update the timestamp for the given mode
        data[mode] = timestamp

        # Write the updated data back to the JSON file
        with open(TIMESTAMP_FILE, 'w') as file:
            json.dump(data, file, indent=4)

if __name__ == "__main__":
    app = App()
    app.sync_orders()
