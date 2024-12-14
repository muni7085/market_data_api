from datetime import date, datetime, timezone

import pytest
from sqlmodel import Session, SQLModel, create_engine

from app.data_layer.database.crud.postgresql.user_crud import (
    create_or_update_user_verification,
    create_user,
    delete_user,
    get_user,
    get_user_by_attr,
    get_user_verification,
    is_attr_data_in_db,
    update_user,
)
from app.data_layer.database.models.user_model import User, UserVerification


@pytest.fixture(scope="module")
def engine():
    """
    Fixture to create an in-memory SQLite database engine for testing.

    Using an in-memory database speeds up tests by avoiding disk I/O.
    """
    engine = create_engine("sqlite:///:memory:")
    SQLModel.metadata.create_all(engine)

    yield engine

    engine.dispose()


@pytest.fixture(scope="function")
def session(engine):
    """
    Fixture to provide a new database session for each test function.

    Ensures each test runs in isolation with a clean database state.
    """
    with Session(engine) as session:
        yield session


@pytest.fixture
def test_user():
    """
    Fixture to create a test user object.

    Returns a User instance with predefined attributes for testing.
    """
    return User(
        user_id=12356789012,
        username="testuser",
        email="testuser@example.com",
        password="password123",
        date_of_birth=date(1990, 1, 1),
        phone_number="1234567890",
        gender="male",
    )


def test_create_user(session, test_user):
    """
    Test creating a new user.
    Ensures `create_user` adds a user to the database.
    """
    result = create_user(test_user, session)
    assert result is True

    # Verify the user was added to the database
    user = get_user(test_user.user_id, session)
    assert user.user_id == test_user.user_id

    # Attempt to create the same user again
    assert create_user(test_user.copy(), session) is False


def test_get_user(session, test_user):
    """
    Test retrieving a user by user_id.
    Confirms that `get_user` fetches the correct user.
    """
    user = get_user(test_user.user_id, session)

    assert user.user_id == test_user.user_id


def test_is_attr_data_in_db(session):
    """
    Test if attribute data exists in the database.
    Verifies that `is_attr_data_in_db` detects existing attributes.
    """
    result = is_attr_data_in_db(User, {"email": "testuser@example.com"}, session)

    assert result == {"message": "email already exists"}


def test_get_user_by_attr(session, test_user):
    """
    Test retrieving a user by attribute.

    Checks that `get_user_by_attr` returns the correct user.
    """
    create_user(test_user, session)
    user = get_user_by_attr("email", "testuser@example.com", session)

    assert user.email == "testuser@example.com"


def test_update_user(session, test_user):
    """
    Test updating a user's information.

    Verifies that `update_user` modifies the user's data.
    """
    create_user(test_user, session)
    updated_user = update_user(
        test_user.user_id, {"username": "updated_test_user"}, session
    )

    assert updated_user.username == "updated_test_user"


def test_delete_user(session, test_user):
    """
    Test deleting a user.

    Checks that `delete_user` removes the user from the database.
    """
    create_user(test_user, session)
    result = delete_user(test_user.user_id, session)

    assert result is True

    # Verify the user no longer exists
    user = get_user(test_user.user_id, session)
    assert user is None


def test_get_user_verification(session):
    """
    Test retrieving a user verification object.

    Ensures `get_user_verification` retrieves the correct verification.
    """
    user_verification = UserVerification(
        recipient="testuser@example.com",
        verification_code="123456",
        expiration_time=datetime.now(timezone.utc).timestamp(),
        reverified_datetime="2023-12-01T12:00:00",
        verification_medium="email",
    )
    create_or_update_user_verification(user_verification, session)
    result = get_user_verification("testuser@example.com", session)

    assert result.recipient == "testuser@example.com"


def test_create_or_update_user_verification(session):
    """
    Test creating or updating a user verification object.

    Verifies that verification data is correctly added or updated.
    """
    user_verification = UserVerification(
        recipient="testuser@example.com",
        verification_code="123456",
        expiration_time=datetime.now(timezone.utc).timestamp(),
        reverified_datetime="2023-12-01T12:00:00",
        verification_medium="email",
    )
    create_or_update_user_verification(user_verification, session)

    # Update the verification code
    updated_verification = UserVerification(
        recipient="testuser@example.com",
        verification_code="654321",
        expiration_time=datetime.now(timezone.utc).timestamp(),
        reverified_datetime="2024-12-01T12:00:00",
        verification_medium="email",
    )
    create_or_update_user_verification(updated_verification, session)
    result = get_user_verification("testuser@example.com", session)

    assert result.verification_code == "654321"
