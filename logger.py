import os
import json
from datetime import datetime


class Logger:
    LOG_FILE_PATH = "api_log.txt"
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

        if not os.path.exists(self.LOG_FILE_PATH):
            open(self.LOG_FILE_PATH, 'w').close()

        # Open (or create) the log file and append the message
        with open(self.LOG_FILE_PATH, "a") as log_file:
            log_file.write(timestamp + message + "\n")


    def check_log_size(self):
        # Check if the log file exists
        if os.path.exists(self.LOG_FILE_PATH):
            with open(self.LOG_FILE_PATH, "r+") as log_file:
                lines = log_file.readlines()
                if len(lines) > self.MAX_LOG_LINES:
                    # If there are too many lines, keep only the latest MAX_LOG_LINES lines
                    trimmed_lines = lines[-self.MAX_LOG_LINES:]
                    log_file.seek(0)  # Move the pointer to the beginning of the file
                    log_file.writelines(trimmed_lines)
                    log_file.truncate()  # Truncate the file to the current size
                    print("Log file trimmed to the last", self.MAX_LOG_LINES, "lines.")
