from fastapi import APIRouter, Depends
from app.schemas.user_model import UserSignup, UserSignIn
from .authenticate import (
    signup_user,
    signin_user,
    get_current_user,
    generate_verification_code,
    update_user_verification_status,
)
from datetime import datetime, timedelta, timezone
from app.data_layer.database.crud.postgresql.user_crud import (
    create_or_update_email_verification,
    get_email_verification,
    get_user_by_field,
)
from app.data_layer.database.models.user_model import EmailVerification
from app.notification.email.providers import BrevoEmailProvider


router = APIRouter(prefix="/authentication", tags=["authentication"])

# Define OAuth2 scheme with token URL


@router.post("/signup")
async def signup(user: UserSignup):
    return signup_user(user)


@router.post("/signin")
async def signin(user: UserSignIn):
    return signin_user(user.email, user.password)


@router.get("/send-verification-code")
async def send_verification_code(email: str):
    user = get_user_by_field("email", email)
    if user is None:
        return {"message": "User does not exist with this email"}
    if user.is_verified:
        return {"message": "Email is already verified"}

    code = generate_verification_code()
    create_or_update_email_verification(
        EmailVerification(
            email=email,
            verification_code=code,
            expiration_time=int(
                (datetime.now(timezone.utc) + timedelta(minutes=10)).timestamp()
            ),
        )
    )
    email_provider = BrevoEmailProvider()
    email_provider.send_notification(code, email, user.username)
    return {"message": f"Verification code sent to {email}. Valid for 10 minutes"}


@router.get("/verify-code")
async def verify_email(email: str, verification_code: str):
    email_verification = get_email_verification(email)
    if email_verification.verification_code == verification_code:
        if email_verification.expiration_time < int(
            datetime.now(timezone.utc).timestamp()
        ):
            return {"message": "Verification code has expired. Try again"}

        update_user_verification_status(email)

        return {"message": "Email verified successfully"}
    else:
        return {"message": "Invalid verification code"}


@router.get("/protected-endpoint")
def protected_route(current_user: dict = Depends(get_current_user)):
    return {"message": "This is a protected route", "user": current_user}
