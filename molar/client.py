# std
from datetime import datetime, timedelta
import logging
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

# external
from fastapi import HTTPException
from jose import jwt
import pandas as pd
from pydantic import BaseModel, EmailStr
import requests
from requests import models
from requests.api import head
from rich.logging import RichHandler

# molar
import molar
from molar.backend import schemas

from .client_config import ClientConfig
from .exceptions import MolarBackendError

FORMAT = "%(message)s"
logging.basicConfig(
    level="INFO", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)


class Client:
    def __init__(self, cfg: ClientConfig):
        self.cfg = cfg
        self.logger = logging.getLogger("molar")
        if self.logger:
            self.logger.setLevel(self.cfg.log_level)
        self.__headers: Dict[str, str] = {}
        self.__token: Optional[str] = None

        # TODO need to perform some parsing
        # TODO compare to the current client python/molar version
        # if not (user_header == "molar v0.3 python v2.7.3"):
        #     self.logger.debug("Current Client is out of date")

    @property
    def token(self):
        if self.__token is None:
            token = self.authenticate()
            self.__token = token

        claims = jwt.get_unverified_claims(self.__token)
        exp = datetime.fromtimestamp(claims["exp"])

        if exp + timedelta(seconds=30) < datetime.utcnow():
            token = self.authenticate()
            self.__token = token
        return self.__token

    @property
    def headers(self):
        if "Authorization" not in self.__headers.keys():
            self.__headers["Authorization"] = f"Bearer {self.token}"
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

        response = requests.request(
            method,
            f"{self.cfg.base_url}{url}",
            params=params,
            json=json,
            data=data,
            headers=headers,
        )
        
        if response.status_code == 500:
            raise MolarBackendError(status_code=500, message="Server Error")

        out = response.json()

        if response.status_code != 200:
            raise MolarBackendError(
                status_code=response.status_code, message=out["detail"]
            )

        if return_pandas_dataframe:
            return pd.DataFrame.from_records(out)

        if out is not None and "msg" in out.keys():
            self.logger.info(out["msg"])
            return out

        return out

    """
    USER RELATED ACTIONS
    """

    def authenticate(self):
        response = self.request(
            f"/login/access-token",
            method="POST",
            params={"database_name": self.cfg.database_name},
            data={
                "username": self.cfg.username,
                "password": self.cfg.password,
            },
        )
        return response["access_token"]

    def test_token(self):
        return self.request(
            "/login/test-token",
            method="POST",
            params={"database_name": self.cfg.database_name},
            headers=self.headers,
        )

    def test_email(self, email: EmailStr):
        return self.request(
            "/utils/test-emails",
            method="POST",
            params={"email_to": email},
            headers=self.headers,
        )

    def recover_password(self, email: EmailStr):
        return self.request(f"/password-recovery/{email}", method="POST")

    def reset_password(self, token: str, new_password: str):
        data = {
            "token": token,
            "new_password": new_password,
        }
        return self.request("/reset-password", method="POST", data=data)

    """
    DATABASE RELATED ACTIONS
    """

    def database_creation_request(
        self, database_name: str, alembic_revisions: List[str]
    ):
        databasemodel = {
            "database_name": database_name,
            "superuser_fullname": self.cfg.fullname,
            "superuser_email": self.cfg.username,
            "superuser_password": self.cfg.password,
            "alembic_revisions": alembic_revisions,
        }
        return self.request("/database/request", method="POST", json=databasemodel)

    def get_database_requests(self, return_pandas_dataframe=True):
        return self.request(
            "/database/requests",
            method="GET",
            headers=self.headers,
            return_pandas_dataframe=return_pandas_dataframe,
        )
    
    def get_database_information(self, return_pandas_dataframe=True):
        return self.request(
            "/database/information",
            method="GET",
            headers=self.headers,
            return_pandas_dataframe=return_pandas_dataframe,
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
            f"/database/{database_name}", method="DELETE", headers=self.headers
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

    # should it be possible to store data without type or vice versa
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
        datum = {
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
    def query_multiple_joins_filters(
        self,
        database_name: str,
        type: Union[str, List[str]],
        limit: Optional[int],
        offset: Optional[int],
        joins: Optional[Union[List[schemas.QueryJoin], schemas.QueryJoin]],
        filters: Optional[Union[schemas.QueryFilter, schemas.QueryFilterList]],
        order_by: Optional[str],
    ):
        json = {
            "type": type,
            "limit": limit,
            "offset": offset,
            "joins": joins,
            "filter": filters,
            "order_by": order_by,
        }
        return self.request(
            f"/query/{database_name}",
            method="GET",
            headers=self.headers,
            return_pandas_dataframe=True,
        )
    
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
        # invalid filter
        if not (filter_on and filter_op and filter_value) and (
            filter_on or filter_op or filter_value
        ):
            raise ValueError(
                "Invalid filter values: must either have all filter values or none"
            )

        # invalid join values
        if not join_on and join_type:
            raise ValueError("Must join on something if there is a join type specified")

        json = {
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

    def get_alembic_revisions(self, return_pandas_dataframe=True):
        return self.request(
            "/alembic/revisions",
            method="GET",
            headers=self.headers,
            return_pandas_dataframe=return_pandas_dataframe,
        )

    def alembic_upgrade(self, revision: str, database_name: Optional[str] = None):
        if database_name is None:
            database_name = self.cfg.database_name
        return self.request(
            "/alembic/upgrade",
            method="POST",
            params={
                "database_name": database_name,
                "revision": revision,
            },
            headers=self.headers,
        )

    def alembic_downgrade(self, revision: str, database_name: Optional[str] = None):
        if database_name is None:
            database_name = self.cfg.database_name
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
            "/user/",
            method="GET",
            headers=self.headers,
            return_pandas_dataframe=True,
        )

    def get_user_by_email(self, email:EmailStr):
        return self.request(
            f"/user/{email}",
            method="GET",
            headers=self.headers,
            return_pandas_dataframe=False,
        )

    def add_user(
        self,
        email: EmailStr,
        password: str,
        organization: Optional[str] = None,
        is_active: Optional[bool] = True,
        is_superuser: bool = False,
        full_name: Optional[str] = None,
    ):
        user_create_model = {
            "email": email,
            "password": password,
            "organization": organization,
            "is_active": is_active,
            "is_superuser": is_superuser,
            "full_name": full_name,
            "joined_on": datetime.now().isoformat(),
        }
        # check if current user is superuser is in backend
        return self.request(
            "/user/add",
            json=user_create_model,
            method="POST",
            headers=self.headers,
        )
    
    def register_user(
        self,
        email: EmailStr,
        password: str,
        full_name: str,
    ):
        user_register_model = {
            "full_name": full_name,
            "email": email,
            "password": password
        }
        return self.request(
            "/user/register",
            json=user_register_model,
            method="POST",
            headers=self.headers,
        )
    
    def activate_user(
        self,
        email: EmailStr,
    ):
        return self.request(
            "/user/activate",
            method="PATCH",
            params={"email": email},
            headers=self.headers,
        )
    
    def deactivate_user(
        self,
        email: EmailStr,
    ):
        return self.request(
            "/user/deactivate",
            method="PATCH",
            params={"email": email},
            headers=self.headers,
        )

    def update_user(
        self,
        email: EmailStr,
        password: Optional[str] = None,
        organization: Optional[str] = None,
        is_active: Optional[bool] = False,
        is_superuser: bool = False,
        full_name: Optional[str] = None,
    ):
        user_update_model = {
            "email": email,
            "password": password,
            "organization": organization,
            "is_active": is_active,
            "is_superuser": is_superuser,
            "full_name": full_name,
        }
        return self.request(
            "/user/",
            method="PATCH",
            json=user_update_model,
            headers=self.headers,
            return_pandas_dataframe=False,
        )
    
    def delete_user(
        self,
        email: EmailStr
    ):
        return self.request(
            "/user/",
            method="DELETE",
            params={"email": email},
            headers=self.headers
        )

    """
    DEBUGGING
    """

    def test(self):
        return self.request("/utils/test/api", method="GET")