from datetime import datetime
from uuid import UUID
from requests import models

from requests.api import head
from molar.client_config import Client_Config
import molar
import requests
import logging
import pandas as pd
from pydantic import BaseModel, EmailStr
from typing import Any, Dict, List, Optional, Union
from rich.logging import RichHandler
from fastapi import HTTPException

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

class Client_Interface:
    def __init__(self, cfg: Client_Config):
        self.cfg = cfg
        self.logger = logging.getLogger("molar")
        if self.logger:
            self.logger.setLevel(self.cfg.log_level)
        self.__headers: Dict[str, str] = {}

        # request = requests.post(
        #     f'{self.cfg.SERVER_URL}/login/access-token?database=molar_main', 
        #     data={
        #         "username": "test@molar.tooth",
        #         "password": "tooth",
        #     },
        # )

        # #if the cfg doesnt have a token, its the first login so we need to create a new token
        # if (not self.cfg.token):
        #     #TODO check for the expiry of the token
        #     self.cfg.token = request.json()["access_token"]

        # self.header = {'Authorization': f'Bearer {self.cfg.token}'}

        #TODO change schema for TOken to allow for more entries
        # user_header = request.json()["user_header"]
        
        #TODO need to perform some parsing
        #TODO compare to the current client python/molar version
        # if not (user_header == "molar v0.3 python v2.7.3"):
        #     self.logger.debug("Current Client is out of date")

    @property
    def headers(self):
        if "Authorization" not in self.__headers.keys():
            token = self.authenticate()
            self.__headers["Authorization"] = f"Bearer {token}"
        if "User-Agent" not in self.__headers.keys():
            self.__headers["User-Agent"] = f"Molar v{molar.__version__}"
        return self.__headers

    def request(
        self,
        url: str,
        method: str,
        params=None,
        json=None,
        data=None,
        headers=None,
        return_pandas_dataframe=False,
    ):
        if not url.startswith("/"):
            url = "/" + url
        
        response=requests.request(
            method,
            f"{self.cfg.SERVER_URL}{url}",
            params=params,
            json=json,
            data=data,
            headers=headers,
        )

        out = response.json()

        if response.status_code != 200:
            #Handle errors
            self.logger.error(out["detail"])
                  
        
        if return_pandas_dataframe:
            return pd.DataFrame.from_records(out)

        if "msg" in out.keys():
            self.logger.info(out["msg"])
            return out
        
        return out

    """
    USER RELATED ACTIONS
    """
    def authenticate(self):
        response = self.request(
            f"/login/access-token?database={self.cfg.database_name}",
            method="POST",
            data={
                "username": self.cfg.username, 
                "password": self.cfg.password,
            }
        )
        return response["access_token"]

    def test_email(self, email: EmailStr):
        return self.request(
            "/utils/test-emails",
            method="POST",
            params={"email_to": email},
            headers=self.headers,
        )
    
    @staticmethod
    def recover_password(email: EmailStr):
        #static method because client object cant be created without a password
        #no header because it is a static method
        request = requests.post(f"{Client_Config.SERVER_URL}/password-recovery/{email}")
        return request.json()["msg"]
    
    @staticmethod
    def reset_password(token: str, new_password: str):
        #static method because client object cant be created without a password
        #no header beaause it is a static method
        data={
            "token": token,
            "new_password": new_password,
        }
        request = requests.post(f"{Client_Config.cfg.SERVER_URL}/reset-password", data)
        return request.json()["msg"]


    """
    DATABASE RELATED ACTIONS
    """
    def database_creation_request(self, database_name: str):
        databasemodel = {
            "database_name": database_name,
            "superuser_fullname": self.cfg.fullname,
            "superuser_email": self.cfg.username,
            "superuser_password": self.cfg.password,
            "alembic_revisions": ["fe0318fjfew8afj"]
        }
        return self.request(
            "/database/request",
            method="POST",
            json=databasemodel,
            headers=self.headers
        )
    
    def get_database_requests(self):
        return self.request(
            "/database/requests",
            method="GET",
            headers=self.headers,
            return_pandas_dataframe=True
        )

    def approve_database(self, database_name: str):
        return self.request(
            f"/database/approve/{database_name}",
            method="PUT",
            headers=self.headers,
        )

    def remove_database_request(self, database_name: str):
        return self.request(
            f"/database/request/{database_name}",
            method="DELETE",
            headers=self.headers,
        )
    
    def remove_database(self, database_name):
        return self.request(
            f"/database/{database_name}",
            method="DELETE",
            headers=self.headers
        )

    """
    EVENTSTORE RELATED ACTIONS
    """
    def view_entries(
        self,
        database_name: str,
    ):
        return self.request(
            f"/eventstore/{database_name}",
            method="GET",
            return_pandas_dataframe=True,
            headers=self.headers,
        )
    
    #should it be possible to store data without type or vice versa
    def create_entry(
        self,
        database_name: str,
        type: str,
        data: Dict[str, Any],
    ):
        datum = {
            "type": type,
            "data": data,
        }
        return self.request(
            f"/eventstore/{database_name}",
            method="POST",
            json=datum,
            headers=self.headers,
            return_pandas_dataframe=True,
        )
    
    def update_entry(
        self,
        database_name: str,
        uuid: UUID,
        type: str,
        data: Dict[str, Any],
    ):
        datum = {
            "type": type,
            "data": data,
            "uuid": uuid,
        }
        return self.request(
            f"/eventstore/{database_name}",
            method="PATCH",
            json=datum,
            headers=self.headers,
            return_pandas_dataframe=True,
        )
    
    def delete_entry(
        self,
        database_name: str,
        uuid: UUID,
        type: str,
    ):
        datum={
            "type": type,
            "uuid": uuid,
        }
        return self.request(
            f"/eventstore/{database_name}",
            method="DELETE",
            json=datum,
            headers=self.headers,
            return_pandas_dataframe=True,
        )

    """
    QUERYING RELATED ACTIONS
    """
    def query_database(
        self,
        database_name: str,
        type: Union[str, List[str]],
        limit: Optional[int],
        offset: Optional[int],
        join_on: Optional[str],
        join_type: Optional[str],
        filter_on: Optional[str],
        filter_op: Optional[str],
        filter_value: Optional[str],
        order_by: Optional[str],
    ):
        #invalid filter
        if (not (filter_on and filter_op and filter_value) 
            and (filter_on or filter_op or filter_value)):
            raise ValueError("Invalid filter values: must either have all filter values or none")
        
        #invalid join values
        if (not join_on and join_type):
            raise ValueError("Must join on something if there is a join type specified")

        json={
            "type": type,
            "limit": limit,
            "offset": offset,
            "joins": {
                "type": join_on,
                "join_type": join_type,
            },
            "filter": {
                "type": filter_on,
                "op": filter_op,
                "value": filter_value,
            },
            "order_by": order_by,            
        }

        return self.request(
            f"/query/{database_name}",
            method="GET",
            headers=self.headers,
            return_pandas_dataframe=True,
        )

    """
    ALEMBIC RELATED ACTIONS
    """
    def get_alembic_revision(self):
        return self.request(
            "/alembic/revisions",
            method="GET",
            headers=self.headers,
            return_pandas_dataframe=True
        )
    
    def alembic_upgrade(self, database_name: str, revision: str):
        return self.request(
            "/alembic/upgrade",
            method="POST",
            params={
                "database_name": database_name,
                "revision": revision,
            },
            headers=self.headers,
        )
    
    def alembic_downgrade(self, database_name: str, revision: str):
        return self.request(
            "/alembic/downgrade",
            method="POST",
            params={
                "database_name": database_name,
                "revision": revision,
            },
            headers=self.headers,
        )
    
    """
    USER MANAGEMENT RELATED ACTIONS
    """
    def get_users(self):
        return self.request(
            "/user/get-users",
            method="GET",
            headers=self.headers,
        )
    
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
        response = self.request(
            "/user/add-users",
            method="POST",
            data=user_create_model,
            headers=self.headers,
        )
        if response:
            return f"The user {email} has been created!"
        else:
            return f"The user {email} hasn't been created."

    def get_user_by_id(self, id: int):
        return self.request(
            f"/user/{id}",
            method="GET",
            headers=self.headers,
            return_pandas_dataframe=True,
        )

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
        return self.request(
            f"/user/{id}",
            method="PUT",
            data=user_update_model,
            headers=self.headers,
            return_pandas_dataframe=True
        )

    """
    DEBUGGING
    """
    def test(self):
        return self.request(
            "/utils/test/api",
            method="GET"
        )