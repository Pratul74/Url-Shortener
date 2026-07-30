from .base import AppException

class UserAlreadyExistsException(AppException):
    super().__init__("User already exists.")

class InvalidCredentialsException(AppException):
    super().__init__("Invalid email or password")