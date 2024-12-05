from datetime import datetime

from sqlmodel import TIMESTAMP, Column, Field, SQLModel, text


class User(SQLModel, table=True):
    """
    User model to store user details in the database

    Attributes:
    ----------
    user_id: ``str``
        The unique identifier of the user
    username: ``str``
        The full name of the user
    email: ``str``
        The email address of the user
    password: ``str``
        The hashed password of the user
    date_of_birth: ``str``
        The date of birth of the user
    phone_number: ``str``
        The phone number of the user
    gender: ``str``
        The gender of the user
    is_verified: ``bool``
        A boolean flag to indicate if the user has been verified
        through email or phone number
    """

    user_id: str = Field(unique=True, index=True, primary_key=True)
    username: str
    email: str = Field(unique=True, index=True)
    password: str
    date_of_birth: str
    phone_number: str = Field(unique=True, index=True)
    gender: str
    is_verified: bool = False


class UserVerification(SQLModel, table=True):
    """
    UserVerification model to store user verification details in the database.

    Attributes:
    ----------
    recipient: ``str``
        The email or phone number of the user
    verification_medium: ``str``
        The medium used for verification (email/phone)
    verification_code: ``str``
        The verification code sent to the user
    expiration_time: ``int``
        The expiration time of the verification code in seconds
    verification_datetime: ``datetime``
        The datetime when the user was verified for the first time
    reverified_datetime: ``datetime``
        The reverified datetime, if the user reverified the account
        during the reset password process
    """

    recipient: str = Field(primary_key=True)
    verification_medium: str
    verification_code: str
    expiration_time: int
    verification_datetime: datetime | None = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
    reverified_datetime: datetime | None = Field(
        sa_column=Column(
            TIMESTAMP(timezone=True),
            nullable=True,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
