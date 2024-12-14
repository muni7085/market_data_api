from datetime import datetime, timedelta, timezone
from pathlib import Path

import hydra
from fastapi import APIRouter, Depends, HTTPException, status

from app import ROOT_DIR
from app.data_layer.database.crud.postgresql.user_crud import (
    create_or_update_user_verification,
    get_user_by_attr,
    get_user_verification,
)
from app.data_layer.database.models.user_model import UserVerification
from app.notification.provider import NotificationProvider
from app.schemas.user_model import UserSignIn, UserSignup, UserVerificationRequest
from app.utils.common import init_from_cfg
from app.utils.common.logger import get_logger

from .authenticate import (
    generate_verification_code,
    get_current_user,
    signin_user,
    signup_user,
    update_user_verification_status,
)

# Initialize logging
logger = get_logger(Path(__file__).name)

# Load configuration
with hydra.initialize_config_dir(config_dir=f"{ROOT_DIR}/configs", version_base=None):
    notification_provider_cfg = hydra.compose(config_name="user_verification")

notification_provider = init_from_cfg(
    notification_provider_cfg.user_verifier, base_class=NotificationProvider
)

router = APIRouter(prefix="/authentication", tags=["authentication"])


@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserSignup) -> dict:
    """
    This endpoint is used to register a new user in the system.

    Parameters:
    -----------
    - **user**:
        The user details to be registered in the system
    """
    logger.info("Signup attempt for user: %s", user.email)
    return signup_user(user)


@router.post("/signin", status_code=status.HTTP_200_OK)
async def signin(user: UserSignIn) -> dict:
    """
    This endpoint is used to authenticate a user in the system.

    Parameters:
    -----------
    - **user**:
        The user details to be authenticated in the system
    """
    logger.info("Signin attempt for user: %s", user.email)
    return signin_user(user.email, user.password)


@router.post("/send-verification-code", status_code=status.HTTP_200_OK)
async def send_verification_code(email_or_phone: str, verification_medium: str) -> dict:
    """
    Send a verification code to the user's email or phone number.

    Parameters:
    -----------
    - **email_or_phone** (str): The email or phone number to send the verification code to.
    - **verification_medium** (str): The medium for sending the code ('email' or 'phone').

    Returns:
    --------
    - JSON response indicating whether the code was sent successfully.
    """
    logger.info(
        "Sending verification code to %s using %s", email_or_phone, verification_medium
    )

    # Validate verification medium
    if verification_medium not in {"email", "phone"}:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification medium. Use 'email' or 'phone'.",
        )

    # Fetch the user by attribute
    user = get_user_by_attr(verification_medium, email_or_phone)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist with this email or phone.",
        )

    # Check if the user is already verified
    if user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email or phone is already verified.",
        )

    # Generate and save the verification code
    verification_code = generate_verification_code()
    expiration_time = int(
        (datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp()
    )

    create_or_update_user_verification(
        UserVerification(
            recipient=email_or_phone,
            verification_medium=verification_medium,
            verification_code=verification_code,
            expiration_time=expiration_time,
        )
    )

    # Send the notification
    notification_provider.send_notification(
        code=verification_code,
        recipient_email=email_or_phone,
        recipient_name=user.username,
    )

    return {
        "message": f"Verification code sent to {email_or_phone}. Valid for 10 minutes."
    }


@router.post("/verify-code", status_code=status.HTTP_200_OK)
async def verify_user(request: UserVerificationRequest) -> dict:
    """
    Verify the email or phone of the user using the provided verification code.

    Parameters:
    -----------
    - **request**: UserVerificationRequest
        The request object containing the email or phone and the verification code.
    - **response**: Response
        The FastAPI Response object for setting custom headers or cookies.

    Returns:
    --------
    - JSON response indicating success or failure of the verification.
    """
    logger.info("Verification attempt for %s", request.email_or_phone)

    # Fetch user verification details
    email_verification = get_user_verification(request.email_or_phone)

    if email_verification is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User does not exist with this email or phone",
        )

    # Check if verification code matches
    if email_verification.verification_code != request.verification_code:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid verification code"
        )

    # Check if the verification code has expired
    if email_verification.expiration_time < int(datetime.now(timezone.utc).timestamp()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification code has expired. Try again",
        )

    # Update verification status
    update_user_verification_status(request.email_or_phone)

    return {"message": "Email or phone verified successfully"}


@router.get(
    "/protected-endpoint",
    response_model=dict,
    responses={
        401: {"description": "Not authenticated"},
        403: {"description": "Not authorized"},
    },
)
def protected_route(current_user: dict = Depends(get_current_user)) -> dict:
    """
    Dummy protected route to test the authentication.

    Parameters:
    -----------
    - **current_user** (dict): The current authenticated user.

    Returns:
    --------
    - JSON response indicating the protected route access.
    """
    logger.info("Access to protected route by user: %s", current_user["email"])
    return {"message": "This is a protected route", "user": current_user}
