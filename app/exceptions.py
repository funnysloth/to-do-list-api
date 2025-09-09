class UserNotFoundException(Exception):
    '''
    Exception to throw when the user with the defined username wasn't found in the databse.
    '''
    pass

class InvalidCredentialsException(Exception):
    '''
    Exception to throw when the password provided in login process is invalid for the user with the defined username
    '''
    pass

class ListNotFoundException(Exception):
    """
    Exception to throw when the list wasn't found in the user's lists.
    """
    pass

class ListItemNotFoundException(Exception):
    """
    Exception to throw when the list item wasn't found in the list.
    """
    pass