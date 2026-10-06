from .base import AppException

class UserAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__("User already exists.")
    

class InvalidCredentialsException(AppException):
    def __init__(self):
        super().__init__("Invalid email or password")