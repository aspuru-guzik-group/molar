from typing import Any

from fastapi import APIRouter, Depends
from molar.backend.utils import send_test_email
from pydantic.networks import EmailStr

from .... import models, schemas
from ... import deps

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
