import os

from fastapi.testclient import TestClient
from molar.backend.main import app
from molar.backend.core.config import settings
from molar.backend.schemas import UserCreate

from .utils import login_and_get_headers

client = TestClient(app)
superuser_email = os.getenv("MOLAR_SUPERUSER") or "test@molar.tooth"
superuser_password = os.getenv("MOLAR_PASSWORD") or "tooth"



def test_get_users():
    pass
