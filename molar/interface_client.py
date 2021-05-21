from datetime import datetime
from molar.client_config import Client_Config
import requests
import logging
import pandas as pd
from pydantic import BaseModel, EmailStr
from typing import Optional
from rich.logging import RichHandler
from fastapi import HTTPException

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

class Interface_Client:
    def __init__(
        self,
        hostname: str,
        database: str,
        username: str,
        password: str,
        fullname: str,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.cfg = Client_Config(hostname, database, username, password)

        self.logger = logger or logging.getLogger("molar")
        if self.logger:
            self.logger.setLevel(self.cfg.log_level)

        request = requests.post(
            f'{self.cfg.SERVER_URL}/login/access-token?database=molar_main', 
            data={
                "username": "test@molar.tooth",
                "password": "tooth",
            },
        )

        #if the cfg doesnt have a token, its the first login so we need to create a new token
        if (not self.cfg.token):
            #TODO check for the expiry of the token
            self.cfg.token = request.json()["access_token"]

        self.header = {'Authorization': f'Bearer {self.cfg.token}'}

        #TODO change schema for TOken to allow for more entries
        # user_header = request.json()["user_header"]
        
        #TODO need to perform some parsing
        #TODO compare to the current client python/molar version
        # if not (user_header == "molar v0.3 python v2.7.3"):
        #     self.logger.debug("Current Client is out of date")        

    """
    USER RELATED ACTIONS
    """
    def test_email(self):
        request = requests.post(f"{self.cfg.SERVER_URL}/utils/test-email", self.header)
        return request.json()["msg"]
    
    @staticmethod
    def recover_password(self, email: EmailStr):
        #static method because client object cant be created without a password
        #no header because it is a static method
        request = requests.post(f"{self.cfg.SERVER_URL}/password-recovery/{email}")
        return request.json()["msg"]
    
    @staticmethod
    def reset_password(self, token: str, new_password: str):
        #static method because client object cant be created without a password
        #no header beaause it is a static method
        request = requests.post(f"{self.cfg.SERVER_URL}/reset-password")
        return request.json()["msg"]


    """
    DATABASE RELATED ACTIONS
    """
    def database_creation_request(self, database_name: str):
        databasemodel = {
            "database_name": database_name,
            "superuser_fullname": "",
            "superuser_email": self.cfg.username,
            "superuser_password": self.cfg.password,
            "alembic_revisions": []
        }
        request = requests.post(f"{self.cfg.SERVER_URL}/database/request", databasemodel, self.header)
        return request.json()["msg"]
    
    def get_database_requests(self):
        request = requests.get(f"{self.cfg.SERVER_URL}/database/requests", self.header)
        #TODO return data into PANDAS dataframe
        return request

    def approve_database(self, database_name: str):
        request = requests.put(f"{self.cfg.SERVER_URL}/database/approve/{database_name}", self.header)
        return request.json()["msg"]

    def remove_database_requests(self, database_name: str):
        try:
            request = requests.delete(f"{self.cfg.SERVER_URL}/database/request/{database_name}", self.header)
        except HTTPException as e:
            raise ValueError(e.detail)
        return request.json()["msg"]
    
    def remove_database(self, database_name):
        try:
            request = requests.delete(f"{self.cfg.SERVER_URL}/database/{database_name}", self.header)
        except HTTPException as e:
            return "Database not found!"
        return request.json()["msg"]

    """
    ALEMBIC RELATED ACTIONS
    """
    def get_alembic_revision(self):
        request = requests.get(f"{self.cfg.SERVER_URL}/revisions", self.header)
        #TODO turn data into PANDAS dataframe
        return request
    
    def alembic_upgrade(self, database_name: str, revision: str):
        request = requests.post(f"{self.cfg.SERVER_URL}/upgrade", database_name, revision, self.header)
        return "Database upgraded!"
    
    def alembic_downgrade(self, database_name: str, revision: str):
        request = requests.post(f"{self.cfg.SERVER_URL}/downgrade", database_name, revision, self.header)
        return "Database downgraded!"
    
    """
    USER MANAGEMENT RELATED ACTIONS
    """
    def get_users(self):
        request = requests.get(f"{self.cfg.SERVER_URL}/get-users", self.header)
        #TODO turn data into PANDAS dataframe
        return request 
    
    def add_user(
        self,
        email: EmailStr,
        password: str,
        organization: str,
        is_active: Optional[bool] = True,
        is_superuser: bool = False,
        full_name: Optional[str] = None
    ):
        user_create_model = {
            "email": email,
            "password": password,
            "organization": organization,
            "is_active": is_active,
            "is_superuser": is_superuser,
            "full_name": full_name,
            "joined_on": datetime.now(),
        }
        #check if current user is superuser is in backend
        request = requests.post(f"{self.cfg.SERVER_URL}/add-users", user_create_model, self.header)
        if request is None:
            return f"The user {email} hasn't been created."
        else:
            return f"The user {email} has been created!"

    def get_user_by_id(self, id: int):
        request = requests.get(f"{self.cfg.SERVER_URL}/{id}", self.header)
        #TODO transform user object into PANDAS dataframe
        return request

    def update_user(
        self,
        id: int,
        password: Optional[str] = None,
        organization: Optional[str] = None,
        is_active: Optional[bool] = True,
        is_superuser: bool = False,
        full_name: Optional[str] = None,
    ):
        user_update_model = {
            "password": password,
            "organization": organization,
            "is_active": is_active,
            "is_superuser": is_superuser,
            "full_name": full_name,
        }
        request = requests.put(f"{self.cfg.SERVER_URL}/{id}", user_update_model, self.header)
        #TODO transform user object into PANDAS dataframe
        return request

    """
    DEBUGGING
    """
    def test(self):
        request = requests.get('http://localhost:8000/api/v1/utils/test/api')
        return request.json()["msg"]