from jose import jwt, JWTError, ExpiredSignatureError

from app.core.config import settings
from app.core.exceptions import ExpiredTokenError, InvalidTokenError

def decode_and_validate(token: str) -> dict:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_alg]
        )
    except ExpiredSignatureError:
        raise ExpiredTokenError()
    except JWTError:
        raise InvalidTokenError()
