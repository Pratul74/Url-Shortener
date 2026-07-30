from .base import AppException

class UrlNotFoundException(AppException):
    def __init__(self):
        super().__init__("Url not found.")

class UrlExpiredException(AppException):
    def __init__(self):
        super().__init__("Url has expired.")

class UrlInactiveException(AppException):
    def __init__(self):
        super().__init__("Url is inactive.")

class AliasAlreadyExistsException(AppException):
    def __init__(self):
        super().__init__("Alias already exists.")