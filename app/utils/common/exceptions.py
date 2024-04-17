from fastapi import HTTPException, status


class SymbolNotFoundException(HTTPException):
    """
    SymbolNotFoundException is raised when the given symbol is not found in the stock exchange.
    """

    def __init__(self, symbol: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Symbol {symbol} not found. Please provide a valid symbol. Refer to the NSE symbols list for valid symbols.",
        )


class CredentialsException(HTTPException):
    """
    CredentialsException is raised when the credentials are not set in the environment variable.
    """

    def __init__(self, credential_name: str):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"{credential_name} environment variable is not set.",
        )


class UnkownException(HTTPException):
    """
    UnkownException is raised when an unknown exception occurs.
    This class can be used to raise exceptions that are not handled by the application.
    """

    def __init__(self, error_message: str, status_code: int):
        super().__init__(
            status_code=status_code,
            detail=error_message,
        )
