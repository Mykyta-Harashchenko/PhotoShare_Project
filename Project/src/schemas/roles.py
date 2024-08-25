from pydantic import BaseModel
from enum import Enum


class RoleEnum(str, Enum):
    USER = "User"
    ADMIN = "Admin"
    MODERATOR = "Moderator"


class RoleBase(BaseModel):
    id: int
    name: RoleEnum
