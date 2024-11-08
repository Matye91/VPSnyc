# main.py

# pip install sshtunnel
# pip install requests

# TODO
# load only orders at which the timestamp is younger than the latest sync
# store the login data safe(r)

import requests
import json
import os
from database.sql_server import SQLServerConnection
from database.data_processor import DataProcessor
from config import API_CONFIG

class App:
    def __init__(self):
        # Initialize database connections and data processor
        self.sql_server = SQLServerConnection()
        self.data_processor = DataProcessor()

    def sync_orders(self):

        SQL_QUERY = """
            SELECT Belegdatum AS Datum, Belegnummer AS Auftragsnr, A0Empfaenger AS Kdnr, 
                A0Matchcode AS Kunde, USER_UnserZeichen AS UnserZeichen, Vertreter, USER_Kennung 
                AS Kennung, Nettobetrag AS GesamtNetto, Rabattbetrag1 as Porto
            FROM [OLReweAbf].[dbo].[KHKVKBelege] 
            WHERE Belegart = 'Auftragsbestätigung'
            """

        try:
            # Connect to SQL Server and fetch data
            self.sql_server.connect()
            rows = self.sql_server.fetch_data(SQL_QUERY)
            print("Data fetched from SQL Server.")

            # Process each row and collect it in a list
            data_list = [self.data_processor.process_order_row(row) for row in rows]

            # add the query_type
            payload = {
                "query_type": "sync_orders",
                "data": data_list
            }

            # Send all data in one request
            self.send_to_api(payload)

        except Exception as e:
            print(f"Error: {e}")

        finally:
            # Close database connections
            self.sql_server.close()

    def send_to_api(self, payload):
        # Send the entire data list as JSON payload in one request
        try:
            response = requests.post(API_CONFIG['url'], json=payload, headers=API_CONFIG['headers'])

            # store the response of the API
            response.raise_for_status()

            try:
                results = response.json().get("results", {})
            except json.JSONDecodeError:
                print("Error: The API response is not in JSON format.")
                print("Response text:", response.text)  # Print the raw response for debugging
                exit()

            # Get the path of the current directory where the program is stored
            current_directory = os.path.dirname(os.path.abspath(__file__))
            log_file_path = os.path.join(current_directory, "api_log.txt")

            # Open (or create) the log file and append each result
            with open(log_file_path, "a") as log_file:
                # Log inserted records
                for auftragsnr in results.get("inserted", []):
                    log_file.write(f"Auftragsnr {auftragsnr} erfolgreich eingefügt.\n")

                # Log updated records
                for auftragsnr in results.get("updated", []):
                    log_file.write(f"Auftragsnr {auftragsnr} erfolgreich aktualisiert.\n")

                # Log errors with details
                for error in results.get("errors", []):
                    auftragsnr = error.get("Auftragsnr", "Unknown")
                    error_message = error.get("error", "No error message provided")
                    log_file.write(f"FEHLER: Auftragsnr {auftragsnr}, Message: {error_message}\n")

            print("Log updated successfully.")

        except requests.exceptions.RequestException as e:
            print(f"An error occurred: {e}")

if __name__ == "__main__":
    app = App()
    app.sync_orders()
