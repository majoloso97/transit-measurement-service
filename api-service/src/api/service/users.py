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
        user = self.get_user(by='field', username=username)
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
        existing = self.get_user(by='field', username=user.username)
        if existing:
            raise_http_exception(400,
                                 "User already exists")
        
        user.password = self.hasher.get_password_hash(user.password)
        
        with self.crud.db.get_session() as session:
            created_user = self.crud.create_item(session=session,
                                                 item_create=user)
        
        access_token_kwargs = {"sub": str(created_user.id)}
        access_token = self.hasher.create_access_token(access_token_kwargs)
        return {"access_token": access_token, "token_type": "bearer"}

    def modify_user(self, user_id: int, params: ModifiedUser) -> User:
        user = self.get_user(by='id', item_id=user_id)
        if not user:
            raise_http_exception(404,
                                 "User doesn't exist")
        if params.password:
            params.password = self.hasher.get_password_hash(params.password)

        with self.crud.db.get_session() as session:
            modified = self.crud.update_item(session=session,
                                             item_id=user.id,
                                             item_update=params)
        return modified

    def get_user(self, by: str, **kwargs) -> User:
        methods = {
            'id': self.crud.get_item,
            'field': self.crud.get_item_by_field
        }
        retrieval_method = methods.get(by, None)
        with self.crud.db.get_session() as session:
            user = retrieval_method(session, **kwargs)
        return user
