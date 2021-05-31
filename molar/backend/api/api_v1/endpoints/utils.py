# std
from typing import Any

# external
from fastapi import APIRouter, Depends
from pydantic.networks import EmailStr

# molar
from molar.backend.utils import send_test_email

from ... import deps
from .... import models, schemas

router = APIRouter()


@router.post("/test-email", response_model=schemas.Msg, status_code=201)
def test_email(
    email_to: EmailStr,
    current_user=Depends(deps.get_current_active_superuser),
) -> Any:
    """
    Test emails.
    """
    send_test_email(email_to=email_to)
    return {"msg": "Test email sent"}
