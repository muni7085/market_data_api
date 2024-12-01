from sqlmodel import SQLModel, Field, Column, TIMESTAMP, text

from datetime import datetime


class User(SQLModel, table=True):
    user_id: str = Field(unique=True, index=True, primary_key=True)
    username: str
    email: str = Field(unique=True, index=True)
    password: str
    date_of_birth: str
    phone_number: str = Field(unique=True, index=True)
    gender: str
    is_verified: bool = False


class UserVerification(SQLModel, table=True):
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
