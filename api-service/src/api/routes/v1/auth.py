from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from api.dependencies.auth import refresh_token
from api.service.users import UserManager
from shared.schemas.auth import Token


router = APIRouter(prefix='/api/v1/auth')
user_manager = UserManager()


@router.post('/login/', response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    return user_manager.create_user_token(form_data)


@router.post('/refresh-token/', response_model=Token)
def refresh_token(token_data=Depends(refresh_token)):
    return token_data
