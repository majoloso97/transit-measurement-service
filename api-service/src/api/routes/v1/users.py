from fastapi import APIRouter, Depends
from shared.schemas.users import UserSchema, NewUser, ModifiedUser
from shared.schemas.auth import Token
from api.service.users import UserManager
from api.errors import raise_http_exception
from api.dependencies.auth import get_current_active_user, decode_token


router = APIRouter(prefix='/api/v1/users')
users = UserManager()


@router.post('/')
def create_user(user: NewUser) -> Token:
    return users.create_user(user)


@router.get('/me/', response_model=UserSchema)
def get_current_user(current_user: UserSchema =
                     Depends(get_current_active_user)) -> UserSchema:
    return current_user


@router.get('/{id}/', response_model=UserSchema)
def get_user(id: str,
             valid_token=Depends(decode_token)) -> UserSchema:
    user = users.get_user(user_id=id)
    if user is None:
            raise_http_exception(404,
                                 "User doesn't exist")
    return user


@router.patch('/me/', response_model=UserSchema)
def update_current_user(params: ModifiedUser,
                        current_user: UserSchema =
                            Depends(get_current_active_user)):
    return users.modify_user(user_id=current_user.id,
                             params=params)


@router.patch('/{id}/', response_model=UserSchema)
def modify_user(id: str,
                params: ModifiedUser,
                valid_token=Depends(decode_token)):
    return users.modify_user(user_id=id,
                             params=params)


@router.delete('/me/', response_model=UserSchema)
def deactivate_current_user(current_user: UserSchema =
                                Depends(get_current_active_user)):
    params = ModifiedUser(is_active=False)
    return users.modify_user(user_id=current_user.id,
                             params=params)


@router.delete('/{id}/', response_model=UserSchema)
async def deactivate_user(id: str,
                          valid_token=Depends(decode_token)):
    params = ModifiedUser(is_active=False)
    return users.modify_user(user_id=id,
                             params=params)
