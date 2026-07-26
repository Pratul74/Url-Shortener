from .base import AppException

class UrlNotFoundException(AppException):
    def __int__(self):
        super().__int__("Url not found.")

class UrlExpiredException(AppException):
    def __int__(self):
        super().__int__("Url has expired.")

class UrlInactiveException(AppException):
    def __int__(self):
        super().__int__("Url is inactive.")

class AliasAlreadyExistsException(AppException):
    def __int__(self):
        super().__int__("Alias already exists.")