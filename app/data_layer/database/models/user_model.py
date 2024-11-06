from sqlmodel import Field, SQLModel

class User(SQLModel, table=True):
    """
    This class holds the information about the users

    Attributes
    ----------
    username: ``str``
        The username of the user. This is the primary key
    password: ``str``
        The password of the user
    email: ``str``
        The email of the user
    full_name: ``str``
        The full name of the user
    phone_number: ``str``
        The phone number of the user
    """
    
    username: str = Field(primary_key=True)
    password: str
    email: str
    full_name: str
    phone_number: str

    def to_dict(self):
        """
        Returns the object as a dictionary.
        """
        return {
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "phone_number": self.phone_number
        }