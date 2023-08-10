from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from api.errors import raise_http_exception
from settings import settings


stored_api_key = settings.FAST_API_KEY
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  


def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if api_key != stored_api_key:
        raise_http_exception(401, 'Forbidden')
