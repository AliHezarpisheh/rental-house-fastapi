"""Module defines routers related to totp operations."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, status
from pydantic.functional_validators import BeforeValidator

from app.account.otp.api.dependencies import get_totp_service
from app.account.otp.repository.services import TotpService
from toolkit.api.enums import OpenAPITags
from toolkit.api.schemas import APIResponse

EmailBody = Annotated[str, Body(embed=True, examples=["test@test.com"])]

router = APIRouter(prefix="/users/totp", tags=[OpenAPITags.USERS])


@router.post(
    "/send",
    response_model=APIResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def send_totp(
    email: EmailBody,
    totp_service: Annotated[TotpService, Depends(get_totp_service)],
) -> dict[str, str]:
    """
    Send TOTP to a user.

    This endpoint generates and sends a Time-based One-Time Password (TOTP) to a user
    based on their `email`.

    - **email**: The email of the user to whom the TOTP will be sent.

    The TOTP will be generated by the TOTP service and associated with the user for
    future verification. This could be part of the authentication process for
    securing user actions.

    \f
    Parameters
    ----------
    email : str
        The email of the user to whom the TOTP will be sent.
    totp_service : TotpService
        Injected dependency responsible for generating and sending TOTPs.

    Returns
    -------
    dict
        A dictionary containing a success message.
    """
    result = await totp_service.set_totp(email=email)
    return result


@router.post(
    "/verify",
    response_model=APIResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_200_OK,
)
async def verify_otp(
    email: EmailBody,
    totp: Annotated[
        str, Body(embed=True, examples=["213957", 235092]), BeforeValidator(str)
    ],
    totp_service: Annotated[TotpService, Depends(get_totp_service)],
) -> dict[str, str]:
    """
    Verify TOTP for a user.

    This endpoint verifies the Time-based One-Time Password (TOTP) provided by the user.
    The verification is done by comparing the provided TOTP with the stored value
    associated with the user.

    - **email**: The email of the user to whom the TOTP will be sent.
    - **totp**: The TOTP to verify, provided in the request body.

    If the TOTP is valid, the user is successfully authenticated.

    \f
    Parameters
    ----------
    email : str
        The email of the user to whom the TOTP will be sent.
    totp : str
        The TOTP provided by the user for verification.
    totp_service : TotpService
        Injected dependency responsible for verifying the TOTP.

    Returns
    -------
    dict
        A dictionary containing a success message.
    """
    result = await totp_service.verify_totp(email=email, totp=totp)
    return result
