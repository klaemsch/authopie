from fastapi import status
from fastapi.exceptions import HTTPException

from . import logger


class IncorrectCredentialsException(HTTPException):
    """ HTTPException 401 Unauthorized """

    def __init__(self) -> None:
        """ HTTPException 401 Unauthorized """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="401 Unauthorized: Could not validate credentials",
        )


class TokenValidationFailedException(HTTPException):
    """ HTTPException 401 Unauthorized """

    def __init__(self) -> None:
        """ HTTPException 401 Unauthorized """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="401 Unauthorized: Could not validate Token",
        )


class ActionForbiddenException(HTTPException):
    """ HTTPException 403 Frobidden """

    def __init__(self, scope: str) -> None:
        """ HTTPException 403 Forbidden """
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'403 Forbidden: {scope} is needed to perform this action'
        )


class EntityDoesNotExistException(HTTPException):
    """ HTTPException 404 Not Found """

    def __init__(self, entity_name: str) -> None:
        """ HTTPException 404 Not Found """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'404 Not Found: {entity_name} does not exist'
        )


class EntityAlreadyExistsException(HTTPException):
    """ HTTPException 409 Conflict """

    def __init__(self, entity_name: str) -> None:
        """ HTTPException 409 Conflict """
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'409 Conflict: {entity_name} does already exist'
        )


class TypeException(Exception):
    """
    Gets raised everytime a method expects a certain type but was given another
    """

    def __init__(self, given, expected) -> None:
        """
        Gets raised everytime a method expects a certain type
        but was given another
        """

        # transform not build in types
        if type(expected) is not type:
            expected = expected.__class__

        msg = f'Not a valid {expected}. Got: {given.__class__}'
        logger.error(msg)
        super().__init__(msg)
