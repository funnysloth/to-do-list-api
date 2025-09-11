class UserNotFoundException(Exception):
    """
    Exception raised when a user is not found in the database.
    """
    pass

class InvalidCredentialsException(Exception):
    """
    Exception raised when invalid credentials are provided during authentication.
    """
    pass