from datetime import datetime, timedelta, timezone

import hydra
from fastapi import APIRouter, Depends, Response

from app import ROOT_DIR
from app.data_layer.database.crud.postgresql.user_crud import (
    create_or_update_user_verification,
    get_user_by_attr,
    get_user_verification,
)
from app.data_layer.database.models.user_model import UserVerification
from app.notification.provider import NotificationProvider
from app.schemas.user_model import UserSignIn, UserSignup
from app.utils.common import init_from_cfg

from .authenticate import (
    generate_verification_code,
    get_current_user,
    signin_user,
    signup_user,
    update_user_verification_status,
)

with hydra.initialize_config_dir(config_dir=f"{ROOT_DIR}/configs", version_base=None):
    notification_provider_cfg = hydra.compose(config_name="user_verification")


notification_provider = init_from_cfg(
    notification_provider_cfg.user_verifier, base_class=NotificationProvider
)

router = APIRouter(prefix="/authentication", tags=["authentication"])


@router.post("/signup")
async def signup(user: UserSignup, response: Response):
    """
    This endpoint is used to register a new user in the system.

    Parameters:
    -----------
    - **user**:
        The user details to be registered in the system
    """
    status = signup_user(user)
    response.status_code = status.pop("status_code", 200)

    return status


@router.post("/signin")
async def signin(user: UserSignIn, response: Response):
    """
    This endpoint is used to authenticate a user in the system.

    Parameters:
    -----------
    - **user**:
        The user details to be authenticated in the system
    """
    status = signin_user(user.email, user.password)
    response.status_code = status.pop("status_code", 200)

    return status


@router.get("/send-verification-code")
async def send_verification_code(
    email_or_phone: str, verification_medium: str, response: Response
):
    """
    Send a verification code to the user's email or phone number.

    Parameters:
    -----------
    - **email_or_phone**:
        The email or phone number to send the verification code to
    - **verification_medium**:
        The medium to send the verification code to. Can be either 'email' or 'phone'
    """
    if verification_medium not in ["email", "phone"]:
        response.status_code = 400
        return {"message": "Invalid verification medium. Use 'email' or 'phone'"}

    user = get_user_by_attr(verification_medium, email_or_phone)

    if user is None:
        response.status_code = 404
        return {"message": "User does not exist with this email"}

    if user.is_verified:
        response.status_code = 400
        return {"message": "Email is already verified"}

    code = generate_verification_code()

    create_or_update_user_verification(
        UserVerification(
            recipient=email_or_phone,
            verification_medium=verification_medium,
            verification_code=code,
            expiration_time=int(
                (datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp()
            ),
        )
    )
    notification_provider.send_notification(code, email_or_phone, user.username)
    response.status_code = 200

    return {
        "message": f"Verification code sent to {email_or_phone}. Valid for 10 minutes"
    }


@router.get("/verify-code")
async def verify_email(email: str, verification_code: str, response: Response):
    """
    Verify the email of the user by providing the verification code.

    Parameters:
    -----------
    - **email**:
        The user email to verify
    - **verification_code**:
        The verification code sent to the email
    """
    email_verification = get_user_verification(email)

    if email_verification is None:
        response.status_code = 404
        return {"message": "User does not exist with this email"}

    if email_verification.verification_code == verification_code:
        if email_verification.expiration_time < int(
            datetime.now(timezone.utc).timestamp()
        ):
            response.status_code = 400
            return {"message": "Verification code has expired. Try again"}

        update_user_verification_status(email)
        response.status_code = 200
        return {"message": "Email verified successfully"}

    response.status_code = 400
    return {"message": "Invalid verification code"}


@router.get("/protected-endpoint")
def protected_route(current_user: dict = Depends(get_current_user)):
    """
    Dummy protected route to test the authentication.
    """
    return {"message": "This is a protected route", "user": current_user}
