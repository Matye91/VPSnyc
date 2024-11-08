import os
import json
from datetime import datetime



class Logger:
    LOG_FILE_NAME = "api_log.txt"
    MAX_LOG_LINES = 1000

    def __init__(self):
        self.check_log_size()

    def process_response(self, response):
        # Try to parse the JSON response
        try:
            results = response.json().get("results", {})
        except json.JSONDecodeError:
            # Log an error if the response is not JSON formatted
            self.write_log("Error: The API response is not in JSON format.")
            self.write_log(f"Response text: {response.text}")
            exit()

        # Log inserted records
        for auftragsnr in results.get("inserted", []):
            message = f"Auftragsnr {auftragsnr} erfolgreich eingefügt."
            self.write_log(message)

        # Log updated records
        for auftragsnr in results.get("updated", []):
            message = f"Auftragsnr {auftragsnr} erfolgreich aktualisiert."
            self.write_log(message)

        # Log errors with details
        for error in results.get("errors", []):
            auftragsnr = error.get("Auftragsnr", "Unknown")
            error_message = error.get("error", "No error message provided")
            message = f"FEHLER: Auftragsnr {auftragsnr}, Message: {error_message}"
            self.write_log(message)

        print("Log updated successfully.")

    def write_log(self, message):
        # Generate log messages for each result category
        timestamp = datetime.now().strftime("[%Y-%m-%d %H:%M:%S] ")

        # Get the path of the current directory where the program is stored
        current_directory = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(current_directory, self.LOG_FILE_NAME)

        # Open (or create) the log file and append the message
        with open(log_file_path, "a") as log_file:
            log_file.write(timestamp + message + "\n")


    def check_log_size(self):
        # Get the path of the log file
        current_directory = os.path.dirname(os.path.abspath(__file__))
        log_file_path = os.path.join(current_directory, self.LOG_FILE_NAME)

        # Check if the log file exists
        if os.path.exists(log_file_path):
            with open(log_file_path, "r+") as log_file:
                lines = log_file.readlines()
                if len(lines) > self.MAX_LOG_LINES:
                    # If there are too many lines, keep only the latest MAX_LOG_LINES lines
                    trimmed_lines = lines[-self.MAX_LOG_LINES:]
                    log_file.seek(0)  # Move the pointer to the beginning of the file
                    log_file.writelines(trimmed_lines)
                    log_file.truncate()  # Truncate the file to the current size
                    print("Log file trimmed to the last", self.MAX_LOG_LINES, "lines.")
