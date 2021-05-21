import configparser
import os
from typing import Any, Dict, Optional
from .backend.core.config import settings

class Client_Config:
    token: Optional[str] = None
    SERVER_URL: str = f"http://localhost:8000{settings.API_V1_STR}"
    port: int = 5432
    DEFAULT_DIRECTORY: str = "/"
    log_level: str = "INFO"

    def __init__(
        self,
        hostname: str,
        database: str,
        username: str,
        password: str,  
    ):
        #TODO ADD TOKEN FROM CLIENT_INTERFACE
        # Checking if there already exists an .ini file for this username
        # filepath = os.path.join(Client_Config.DEFAULT_DIRECTORY, "database.ini")
        # config_parser = configparser.ConfigParser() #reading the configurations

        # if (os.path.exists(filepath)):
        #     config_parser.read(filepath)
        #     self.token = config_parser[username]['token']

        # if (not os.path.exists(Client_Config.DEFAULT_DIRECTORY)):
        #     # os.mkdir("/.local")
        #     os.mkdir(Client_Config.DEFAULT_DIRECTORY)       

        # if (not os.path.exists(filepath)):
        #     config_parser[username] = {
        #         'hostname': hostname,
        #         'database': database,
        #         'username': username,
        #         'password': password,
        #     }
        #     with open(filepath, 'w') as configfile:
        #         config_parser.write(configfile)
        # else:
        #     config_parser.read(filepath)
        #     if (not config_parser.has_section(username)):
        #         config_parser[username] = {
        #             'hostname': hostname,
        #             'database': database,
        #             'username': username,
        #             'password': password,
        #         }
        #     with open(filepath, 'a') as configfile:
        #         config_parser.write(configfile)

        # initializing the object's attributes
        self.hostname = hostname
        self.database = database
        self.username = username
        self.password = password