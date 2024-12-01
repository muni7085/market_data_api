from app.schemas.user_model import UserSignup
from app.data_layer.database.models.user_model import User
from app.data_layer.database.crud.postgresql.user_crud import (
    create_user,
    check_field_existence,
    get_user_by_field,
    get_user,
    update_user
)
import re
from fastapi import HTTPException
from datetime import datetime
import bcrypt
import random

import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional
from fastapi import Depends, HTTPException, status
from app.utils.constants import (
    JWT_REFRESH_SECRET,
    JWT_SECRET,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    REFRESH_TOKEN_EXPIRE_DAYS,
)
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication/signin")


class UserSignupError(HTTPException):
    def __int__(self, message: str):
        self.message = message
        super().__init__(self.message)


def validate_email(email: str) -> bool:
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w{2,3}$"

    if re.match(email_regex, email) is None:
        raise UserSignupError("Invalid email format")

    return True


def validate_phone_number(phone_number: str) -> bool:
    phone_number_regex = r"^\d{10}$"
    if re.match(phone_number_regex, phone_number) is None:
        raise UserSignupError(400, "Invalid phone number format")
    return True


def get_hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def validate_password(password: str) -> bool:
    if not (
        len(password) >= 8
        and re.search(r"[A-Z]", password) is not None
        and re.search(r"[a-z]", password) is not None
        and re.search(r"\d+", password) is not None
        and re.search(r"[!@#$%^&*]", password) is not None
    ):

        raise UserSignupError(
            400,
            "Password must be at least 8 characters long and include an uppercase letter, lowercase letter, digit, and special character",
        )
    return True


def verify_password(hash_password: str, confirm_password: str) -> bool:

    if not bcrypt.checkpw(
        confirm_password.encode("utf-8"), hash_password.encode("utf-8")
    ):
        raise UserSignupError(400, "Passwords do not match")

    return True


def validate_gender(gender: str) -> bool:
    if gender.lower() not in ["m", "f", "male", "female"]:
        raise UserSignupError(400, "Gender must be 'M' or 'F'")
    return True


def validate_date_of_birth(date_of_birth: str) -> bool:
    try:
        datetime.strptime(date_of_birth, "%d/%m/%Y")
        return True
    except ValueError:
        raise UserSignupError(
            400, "Invalid date format for date of birth. Expected format: dd/mm/yyyy"
        )


def validate_user_exists(user: UserSignup) -> bool:
    fields_to_check = {
        "email": user.email,
        "phone_number": user.phone_number,
        "user_id": user.user_id,
    }
    response = check_field_existence(User, fields_to_check)
    return response


def validate_user_data(user: UserSignup) -> bool:
    validate_email(user.email)
    validate_phone_number(user.phone_number)
    validate_password(user.password)
    verify_password(get_hash_password(user.password), user.confirm_password)
    validate_gender(user.gender)
    validate_date_of_birth(user.date_of_birth)


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_REFRESH_SECRET, algorithm="HS256")


def decode_token(token: str, secret: str) -> Optional[dict]:
    print(f"Token: {token}")
    print(f"Secret: {secret}")
    try:
        decoded_data = jwt.decode(token, secret, algorithms=["HS256"])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def refresh_access_token(refresh_token: str) -> dict:
    # Decode the refresh token
    decoded_data = decode_token(refresh_token, JWT_REFRESH_SECRET)
    if not decoded_data:
        return {"message": "Invalid or expired refresh token"}, 401

    # Generate a new access token
    access_token = create_access_token(
        {"user_id": decoded_data["user_id"], "email": decoded_data["email"]}
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,  # Optionally return the same refresh token if it hasn't expired
    }


def signup_user(user: UserSignup):
    if reason := validate_user_exists(user):
        return reason
    else:
        validate_user_data(user)

        user_model = User(
            **user.dict(exclude={"password"}), password=get_hash_password(user.password)
        )
        user = create_user(user_model)
        return {
            "message": "User created successfully. Please verify your email to activate your account"
        }


def signin_user(email, password):
    # Check if the user exists
    user = get_user_by_field("email", email)
    if not user:
        return {"message": "Invalid email or password"}, 401

    # Verify the password
    if not verify_password(user.password, password):
        return {"message": "Invalid email or password"}, 401

    if not user.is_verified:
        return {"message": "User is not verified"}, 401

    # Generate tokens
    access_token = create_access_token({"user_id": user.user_id, "email": user.email})
    refresh_token = create_refresh_token({"user_id": user.user_id, "email": user.email})

    # Return tokens to the user
    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def update_user_verification_status(user_email: str, status: bool = True):
    user = get_user_by_field("email", user_email)
    if not user:
        return {"message": "User not found"}, 404

    user.is_verified = status
    update_user(user.user_id, user.model_dump())
    

def generate_verification_code(length: int = 6) -> str:
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        decoded_data = decode_token(token, JWT_SECRET)
        if not decoded_data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Unable to decode token",
            )

        exp_time = decoded_data["exp"]
        current_time = datetime.now(timezone.utc).timestamp()
        if current_time > exp_time:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
            )
        user = get_user(decoded_data["user_id"])
        return user
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )
