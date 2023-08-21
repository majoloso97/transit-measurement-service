import re
from datetime import datetime, timedelta
from passlib.context import CryptContext
from jose import jwt
from settings import settings
from api.errors import raise_http_exception


class PasswordHasher:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password):
        return self.pwd_context.verify(plain_password, hashed_password)

    def test_password_format(self, password):
        lowercase = ''
        uppercase = ''
        special_chars = ''
        number = ''
        error = False
        if len(password) < 8:
            raise_http_exception(400,
                                 'Password must contain at least 8 characters')

        if len(re.findall(r'[a-z]+', password)) == 0:
            error = True
            lowercase = ' one lowercase letter,'

        if len(re.findall(r'[A-Z]+', password)) == 0:
            error = True
            uppercase = ' one uppercase letters,'

        if len(re.findall(r'\W+', password)) == 0:
            error = True
            special_chars = ' one special character,'

        if len(re.findall(r'\d+', password)) == 0:
            error = True
            number = ' one number,'

        message = f'Password must contain at least \
                    {lowercase}{uppercase}{special_chars}{number}'
        message = re.sub(r',\Z', '.', message)

        if error:
            raise_http_exception(400, message)

    def get_password_hash(self, password):
        self.test_password_format(password)
        return self.pwd_context.hash(password)

    def create_access_token(self,
                            data: dict,
                            expires_delta: timedelta =
                            timedelta(minutes=settings.TOKEN_EXPIRATION)):
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode,
                                 settings.SECRET_APP_KEY,
                                 algorithm=settings.JWT_ALGORITHM)
        return encoded_jwt
