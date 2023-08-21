from datetime import datetime
from fastapi.security import OAuth2PasswordRequestForm
from api.service.auth import PasswordHasher
from api.errors import raise_http_exception
from shared.schemas.users import UserSchema, NewUser, ModifiedUser
from shared.database.models import User
from shared.database.crud import CRUDManager


class UserManager:
    def __init__(self) -> None:
        self.hasher = PasswordHasher()
        self.crud = CRUDManager(db_model=User,
                                pydantic_create=NewUser,
                                pydantic_update=ModifiedUser,
                                pydantic_response=UserSchema)

    def authenticate_user(self, username: str, password: str):
        user = self.crud.get_item_by_field(username=username)
        if user is None:
            return False
        if not self.hasher.verify_password(password, user.password):
            return False
        return user

    def create_user_token(self, form_data: OAuth2PasswordRequestForm):
        user = self.authenticate_user(form_data.username,
                                      form_data.password)
        if not user:
            raise_http_exception(401,
                                 "Incorrect username or password",
                                 {"WWW-Authenticate": "Bearer"})
        modified = ModifiedUser(last_active=datetime.utcnow())
        self.modify_user(user_id=user.id, params=modified)
        access_token = self.hasher.create_access_token({"sub": str(user.id)})
        return {"access_token": access_token, "token_type": "bearer"}

    def create_user(self, user: NewUser):
        existing = self.crud.get_item_by_field(username=user.username)
        if existing:
            raise_http_exception(400,
                                 "User already exists")
        
        user.password = self.hasher.get_password_hash(user.password)
        created_user = self.crud.create_item(user)
        access_token_kwargs = {"sub": str(created_user.id)}
        access_token = self.hasher.create_access_token(access_token_kwargs)
        return {"access_token": access_token, "token_type": "bearer"}

    def modify_user(self, user_id: int, params: ModifiedUser) -> User:
        user = self.crud.get_item(item_id=user_id)
        if not user:
            raise_http_exception(404,
                                 "User doesn't exist")
        if params.password:
            params.password = self.hasher.get_password_hash(params.password)

        return self.crud.update_item(item_id=user.id,
                                     item_update=params)

    def get_user(self, user_id: int) -> User:
        user = self.crud.get_item(item_id=user_id)
        if not user:
            raise_http_exception(404,
                                 "User doesn't exist")
        return user
