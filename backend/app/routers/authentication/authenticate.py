import random
import re
from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from app.data_layer.database.crud.postgresql.user_crud import (
    create_user,
    get_user,
    get_user_by_attr,
    is_attr_data_in_db,
    update_user,
)
from app.data_layer.database.models.user_model import User
from app.schemas.user_model import UserSignup
from app.utils.constants import (
    ACCESS_TOKEN_EXPIRE_MINUTES,
    JWT_REFRESH_SECRET,
    JWT_SECRET,
    REFRESH_TOKEN_EXPIRE_DAYS,
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/authentication/signin")


class UserSignupError(HTTPException):
    """
    Exception class for user signup errors. This class is used to raise exceptions
    when there is an error during user signup. This exception raises when there is
    invalid user data.

    Attributes:
    -----------
    message: ``str``
        The error message to be displayed to the user
    """

    def __init__(self, message: str):

        super().__init__(status.HTTP_400_BAD_REQUEST, message)


def validate_email(email: str) -> bool:
    """
    This function validates the email format. It allows only email addresses with
    the domain 'gmail.com'.

    Parameters:
    -----------
    email: ``str``
        The email address to be validated

    Returns:
    --------
    ``bool``
        True if the email is valid
    """
    email_regex = r"^[\w\.-]+@gmail\.com$"

    if re.match(email_regex, email) is None:
        raise UserSignupError("Invalid email format")

    return True


def validate_phone_number(phone_number: str) -> bool:
    """
    This function validates the phone number format. It allows only phone numbers
    with 10 digits.

    Parameters:
    -----------
    phone_number: ``str``
        The phone number to be validated

    Returns:
    --------
    ``bool``
        True if the phone number is valid
    """
    phone_number_regex = r"^\d{10}$"

    if re.match(phone_number_regex, phone_number) is None:
        raise UserSignupError("Invalid phone number format")

    return True


def get_hash_password(password: str) -> str:
    """
    It hashes the password using bcrypt and returns the hashed password.

    Parameters:
    -----------
    password: ``str``
        The password to be hashed

    Returns:
    --------
    ``str``
        The hashed password
    """
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def validate_password(password: str) -> bool:
    """
    Validates the password format. The password must be at least 8 characters long
    and include an uppercase letter, lowercase letter, digit, and special character.

    Parameters:
    -----------
    password: ``str``
        The password to be validated

    Returns:
    --------
    ``bool``
        True if the password is valid
    """

    if not (
        len(password) >= 8
        and re.search(r"[A-Z]", password) is not None
        and re.search(r"[a-z]", password) is not None
        and re.search(r"\d+", password) is not None
        and re.search(r"[!@#$%^&*]", password) is not None
    ):

        raise UserSignupError(
            "Password must be at least 8 characters long and include an uppercase letter, "
            "lowercase letter, digit, and special character",
        )
    return True


def verify_password(password: str, hash_password: str) -> bool:
    """
    Verifies the password by comparing the hashed password with the password.

    Parameters:
    -----------
    password: ``str``
        The password to be verified
    hash_password: ``str``
        The hashed password to be compared with the password

    Returns:
    --------
    ``bool``
        True if the password matches the hashed password
    """
    if not bcrypt.checkpw(password.encode("utf-8"), hash_password.encode("utf-8")):
        raise UserSignupError("Passwords do not match")

    return True


def validate_gender(gender: str) -> bool:
    """
    Validates the user gender input.

    Parameters:
    -----------
    gender: ``str``
        Gender of the user. It must be 'M' or 'F' (case-insensitive)

    Returns:
    --------
    ``bool``
        True if the given gender in the correct format
    """
    if gender.lower() not in ["m", "f", "o"]:
        raise UserSignupError("Gender must be 'M' or 'F'")

    return True


def validate_date_of_birth(date_of_birth: str) -> bool:
    """
    Validates the date of birth format. The date of birth must be in the format
    'dd/mm/yyyy' and a valid date.

    Parameters:
    -----------
    date_of_birth: ``str``
        The date of birth to be validated

    Returns:
    --------
    ``bool``
        True if the date of birth is valid
    """
    try:
        datetime.strptime(date_of_birth, "%d/%m/%Y")
        return True
    except ValueError as exc:
        raise UserSignupError(
            "Invalid date format for date of birth. Expected format: dd/mm/yyyy",
        ) from exc


def validate_user_exists(user: UserSignup) -> dict | None:
    """
    Checks if the user already exists in the database. It checks the email, phone number,
    and user_id fields to see if the user already exists.

    Parameters:
    -----------
    user: ``UserSignup``
        The user details to be checked

    Returns:
    --------
    ``str | None``
        An error message if the user already exists, otherwise None
    """

    fields_to_check = {
        "email": user.email,
        "phone_number": user.phone_number,
        "user_id": user.user_id,
    }
    response = is_attr_data_in_db(User, fields_to_check)

    if response:
        response = {"message": response, "status_code": 400}

    return response


def validate_user_data(user: UserSignup) -> None:
    """
    Validates the user data. If any of the user data is invalid, it raises an exception.

    Parameters:
    -----------
    user: ``UserSignup``
        The user details to be validated
    """
    validate_email(user.email)
    validate_phone_number(user.phone_number)
    validate_password(user.password)
    verify_password(user.confirm_password, get_hash_password(user.password))
    validate_gender(user.gender)
    validate_date_of_birth(user.date_of_birth)


def create_access_token(data: dict) -> str:
    """
    Creates a JWT access token with the given data and expiration time.

    Parameters:
    -----------
    data: ``dict``
        The data to be encoded in the token

    Returns:
    --------
    ``str``
        The JWT access token
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, JWT_SECRET, algorithm="HS256")


def create_refresh_token(data: dict) -> str:
    """
    Creates a JWT refresh token with the given data and expiration time.
    It can be used to generate a new access token when the access token expires.

    Parameters:
    -----------
    data: ``dict``
        The data to be encoded in the token

    Returns:
    --------
    ``str``
        The JWT refresh token
    """

    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire})

    return jwt.encode(to_encode, JWT_REFRESH_SECRET, algorithm="HS256")


def decode_token(token: str, secret: str) -> Optional[dict]:
    """
    Decodes the given token using the secret key and returns the decoded data.

    Parameters:
    -----------
    token: ``str``
        The token to be decoded
    secret: ``str``
        The secret key used to decode the token

    Returns:
    --------
    ``Optional[dict]``
        The decoded data from the token
    """
    try:
        decoded_data = jwt.decode(token, secret, algorithms=["HS256"])
        return decoded_data
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def access_token_from_refresh_token(refresh_token: str) -> dict:
    """
    Create the access token using the refresh token. If the refresh token is invalid
    or expired, it returns an error message. Otherwise, it generates a new access token
    and returns it.

    Parameters:
    -----------
    refresh_token: ``str``
        The refresh token to generate a new access token

    Returns:
    --------
    ``dict``
        A dictionary containing the new access token and the refresh token
    """
    decoded_data = decode_token(refresh_token, JWT_REFRESH_SECRET)

    if not decoded_data:
        return {"message": "Invalid or expired refresh token", "status_code": 401}

    # Generate a new access token
    access_token = create_access_token(
        {"user_id": decoded_data["user_id"], "email": decoded_data["email"]}
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }


def signup_user(user: UserSignup):
    """
    Validates the user data and creates a new user in the system if the user does not
    already exist. If the user already exists, it returns an error message.

    Parameters:
    -----------
    user: ``UserSignup``
        The user details to be registered in the system

    Returns:
    --------
    ``dict``
        A message indicating if the user was created successfully or an error message
    """
    if reason := validate_user_exists(user):
        return reason

    validate_user_data(user)

    user_model = User(
        **user.dict(exclude={"password"}), password=get_hash_password(user.password)
    )
    create_user(user_model)

    return {
        "message": "User created successfully. Please verify your email to activate your account",
        "status_code": 200,
    }


def signin_user(email, password):
    """
    Sign in the user with the given email and password. If the user does not exist or
    the password is incorrect, it returns an error message. If the user is not verified,
    it returns a message indicating that the user is not verified and cannot sign in.

    If the user exists and the password is correct, it generates an access token and a
    refresh token and returns them to the user.

    Parameters:
    -----------
    email: ``str``
        The email address of the user
    password: ``str``
        The password of the user

    Returns:
    --------
    ``dict``
        A message indicating if the login was successful or an error message
    """

    user = get_user_by_attr("email", email)
    if not user:
        return {"message": "Invalid email or password", "status_code": 401}

    if not verify_password(password, user.password):
        return {"message": "Invalid email or password", "status_code": 401}

    if not user.is_verified:
        return {"message": "User is not verified", "status_code": 401}

    access_token = create_access_token({"user_id": user.user_id, "email": user.email})
    refresh_token = create_refresh_token({"user_id": user.user_id, "email": user.email})

    return {
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "status_code": 200,
    }


def update_user_verification_status(user_email: str, status: bool = True):
    """
    Update the user verification status in the database. If the user does not exist,
    it returns an error message.

    Parameters:
    -----------
    user_email: ``str``
        The email address of the user
    status: ``bool``
        The verification status of the user
    """
    user = get_user_by_attr("email", user_email)
    if not user:
        return {"message": "User not found", "status_code": 401}

    user.is_verified = status
    update_user(user.user_id, user.model_dump())

    return {"message": "User verified successfully", "status_code": 200}


def generate_verification_code(length: int = 6) -> str:
    """
    Generate a random verification code consisting of numbers only with the given length.

    Parameters:
    -----------
    length: ``int``
        The length of the verification code to be generated

    Returns:
    --------
    ``str``
        The generated verification code
    """
    return "".join([str(random.randint(0, 9)) for _ in range(length)])


def get_current_user(token: str = Depends(oauth2_scheme)):
    """
    Retrieve the current user from the database using the access token. If the token
    is invalid or expired, it returns an error message. If the token is valid, it
    retrieves the user details from the database and returns the user.

    Parameters:
    -----------
    token: ``str``
        The access token to retrieve the user details

    Returns:
    --------
    ``User``
        The user details retrieved from the database
    """
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

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        ) from e

    return user
