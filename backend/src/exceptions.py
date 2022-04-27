from fastapi import status
from fastapi.exceptions import HTTPException


class IncorrectCredentialsException(HTTPException):
    """ HTTPException 401 Unauthorized """

    def __init__(self) -> None:
        """ HTTPException 401 Unauthorized """
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )


class ActionForbiddenException(HTTPException):
    """ HTTPException 403 Frobidden """

    def __init__(self, scope: str) -> None:
        """ HTTPException 403 Frobidden """
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f'{scope} is needed to perform this action'
        )


class EntityDoesNotExistException(HTTPException):
    """ HTTPException 404 Not Found """

    def __init__(self, entity_name: str) -> None:
        """ HTTPException 404 Not Found """
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'{entity_name} does not exist'
        )


class EntityAlreadyExistsException(HTTPException):
    """ HTTPException 409 Conflict """

    def __init__(self, entity_name: str) -> None:
        """ HTTPException 409 Conflict """
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=f'{entity_name} does already exist'
        )
