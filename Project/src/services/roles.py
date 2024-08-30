from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from Project.src.database.db import get_db
from Project.src.entity.models import User
from Project.src.services.auth import auth_service  # TODO:

from Project.src.schemas.roles import RoleEnum

import logging

logger = logging.getLogger(__name__)


class RoleChecker:
    """
    A dependency class that checks whether the current user has one of the allowed roles.

    :param allowed_roles: A list of roles that are allowed to access the endpoint.
    :type allowed_roles: list[RoleEnum]

    :raises HTTPException: If the user's role is not in the allowed roles.
    """

    def __init__(self, allowed_roles: list[RoleEnum]):
        """
        Initialize the RoleChecker with the allowed roles.

        :param allowed_roles: The roles that are allowed to access the endpoint.
        :type allowed_roles: list[RoleEnum]
        """
        self.allowed_roles = allowed_roles

    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

    async def __call__(self, token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)) -> User:
        """
        Validate the user's role.

        :param token: The OAuth2 token from the request.
        :type token: str
        :param db: The database session.
        :type db: AsyncSession
        :return: The authenticated user.
        :rtype: User
        :raises HTTPException: If the user's role is not allowed to access the endpoint.
        """
        user = await auth_service.get_current_user(token, db)
        logger.info(f"User role: {user.role.name}, Allowed roles: {[role.name for role in self.allowed_roles]}")
        if user.role.name not in [role.name for role in self.allowed_roles]:
            logger.warning("Permission denied")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to perform this action"
            )
        return user
