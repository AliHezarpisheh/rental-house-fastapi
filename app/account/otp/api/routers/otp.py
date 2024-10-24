"""Module defines routers related to otp."""

from typing import Annotated

from fastapi import APIRouter, Body, Depends, Path, status
from pydantic.functional_validators import BeforeValidator

from app.account.otp.api.dependencies import get_totp_service
from app.account.otp.repository.services import TotpService
from toolkit.api.enums import OpenAPITags
from toolkit.api.schemas import APIResponse

router = APIRouter(tags=[OpenAPITags.USERS])


@router.post(
    "/users/{user_id}/otp/send",
    response_model=APIResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def send_otp(
    user_id: Annotated[int, Path()],
    totp_service: Annotated[TotpService, Depends(get_totp_service)],
) -> dict[str, str]:
    """
    Send OTP to a user.

    This endpoint generates and sends a Time-based One-Time Password (TOTP) to a user
    based on their `user_id`.

    - **user_id**: The unique identifier of the user to whom the OTP will be sent.

    The OTP will be generated by the TOTP service and associated with the user for
    future verification. This is part of the authentication process for securing user
    actions.

    \f
    Parameters
    ----------
    user_id : int
        The unique identifier of the user to whom the OTP will be sent.
    totp_service : TotpService
        Injected dependency responsible for generating and sending OTPs.

    Returns
    -------
    dict
        A dictionary containing a success message.
    """
    result = await totp_service.set_otp(user_id=user_id)
    return result


@router.post(
    "/users/{user_id}/otp/verify",
    response_model=APIResponse,
    response_model_exclude_none=True,
    status_code=status.HTTP_201_CREATED,
)
async def verify_otp(
    user_id: Annotated[int, Path()],
    totp: Annotated[
        str, Body(embed=True, examples=["213957", 235092]), BeforeValidator(str)
    ],
    totp_service: Annotated[TotpService, Depends(get_totp_service)],
) -> dict[str, str]:
    """
    Verify OTP for a user.

    This endpoint verifies the Time-based One-Time Password (TOTP) provided by the user.
    The verification is done by comparing the provided TOTP with the stored value
    associated with the user.

    - **user_id**: The unique identifier of the user whose OTP is being verified.
    - **totp**: The TOTP to verify, provided in the request body.

    If the OTP is valid, the user is successfully authenticated.

    \f
    Parameters
    ----------
    user_id : int
        The unique identifier of the user whose OTP is being verified.
    totp : str
        The TOTP provided by the user for verification.
    totp_service : TotpService
        Injected dependency responsible for verifying the OTP.

    Returns
    -------
    dict
        A dictionary containing a success message.
    """
    result = await totp_service.verify_totp(user_id=user_id, totp=totp)
    return result
