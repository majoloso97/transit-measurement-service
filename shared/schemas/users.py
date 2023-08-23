from datetime import datetime, timezone
from typing import Optional
from pydantic import EmailStr, BaseModel, ConfigDict


class BaseUser(BaseModel):
    id: Optional[int] = None


class UserSchema(BaseUser):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    password: str
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    description: Optional[str] = None
    photo: Optional[str] = None
    created_at: datetime
    last_active: datetime
    is_active: bool


class NewUser(BaseUser):
    username: str
    password: str
    created_at: datetime = datetime.now(tz=timezone.utc)
    last_active: datetime = datetime.now(tz=timezone.utc)
    is_active: bool = True


class ModifiedUser(BaseUser):
    password: Optional[str] = None
    email: Optional[EmailStr] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    description: Optional[str] = None
    photo: Optional[str] = None
    is_active: Optional[bool] = None
    last_active: Optional[datetime] = None
