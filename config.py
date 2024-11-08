# config.py

# run in terminal to set system variables, then restart the IDE
# setx VPSYNC_SQL_SERVER_HOST "host-ip, port"
# setx VPSYNC_SQL_SERVER_DATABASE "database"
# setx VPSYNC_SQL_SERVER_USER "username"
# setx VPSYNC_SQL_SERVER_PASSWORD "password"

import os

SQL_SERVER_CONFIG = {
    'server': os.getenv("VPSYNC_SQL_SERVER_HOST"),
    'database': os.getenv("VPSYNC_SQL_SERVER_DATABASE"),
    'username': os.getenv("VPSYNC_SQL_SERVER_USER"),
    'password': os.getenv("VPSYNC_SQL_SERVER_PASSWORD"),
    'drivers': [
        "ODBC Driver 18 for SQL Server",
        "ODBC Driver 17 for SQL Server"
    ]
}

API_CONFIG = {
    'url': 'https://www.panda-office.at/WPv2019/wp-content/themes/PandaTheme2022/api/index.php',
    'headers': {
        'Content-Type': 'application/json',
    }
}

