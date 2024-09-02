from pydantic import BaseModel
from enum import Enum


class RoleEnum(str, Enum):
    user = "User"
    admin = "Admin"
    moderator = "Moderator"


class RoleBase(BaseModel):
    id: int
    name: RoleEnum
