from datetime import datetime
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from settings import settings
from shared.schemas.auth import TokenData
from shared.schemas.users import UserSchema, ModifiedUser
from api.errors import raise_http_exception
from api.service.users import UserManager
from api.service.auth import PasswordHasher
from jose import jwt, JWTError


users = UserManager()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
hasher = PasswordHasher()


def decode_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token,
                             settings.SECRET_APP_KEY,
                             algorithms=[settings.JWT_ALGORITHM])
        if list(payload.keys()) == ['sub', 'exp']:
            return payload
        raise_http_exception(401, "Invalid token",
                             headers={"WWW-Authenticate": "Bearer"})
    except JWTError as e:
        raise_http_exception(401,
                             f"Could not validate credentials: {e}",
                             headers={"WWW-Authenticate": "Bearer"})


def get_current_active_user(payload:
                            dict = Depends(decode_token)) -> UserSchema:
    id: int = payload.get("sub")
    if id is None:
        raise_http_exception(
            401,
            "Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"})
    token_data = TokenData(user_id=id)

    user = users.get_user(by='id', item_id=token_data.user_id)
    if user is None:
        raise_http_exception(401,
                             "Could not validate credentials",
                             headers={"WWW-Authenticate": "Bearer"})

    if not user.is_active:
        raise raise_http_exception(400, "Inactive user")

    modified = ModifiedUser(last_active=datetime.utcnow())
    users.modify_user(user_id=user.id, params=modified)
    return user


def refresh_token(current_user: str = Depends(get_current_active_user)):
    access_token = hasher.create_access_token({"sub": str(current_user.id)})
    return {"access_token": access_token, "token_type": "bearer"}
