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