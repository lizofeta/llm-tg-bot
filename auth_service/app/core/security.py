from datetime import datetime, timezone, timedelta

from jose import jwt, JWTError, ExpiredSignatureError
from passlib.context import CryptContext

from app.core.exceptions import InvalidTokenError, ExpiredTokenError

pwd_context = CryptContext(schemes=["bcrypt", "argon2"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(
        data: dict,
        expire_minutes: int,
        secret: str,
        algorithm: str 
) -> str:
    """
    Создает jwt access token 

    data: dict - часть payload с полями "sub" & "role"
    expire_minutes: int - время жизни токена в минутах
    secret: str - jwt secret
    algorithm: str - алгоритм шифрования 
    """
    now = datetime.now(timezone.utc)

    payload = {
        **data,
        "exp": now + timedelta(minutes=expire_minutes),
        "iat": now
    }

    return jwt.encode(
        payload,
        secret,
        algorithm
    )

def decode_token(
        token: str,
        secret: str,
        algorithm: str
) -> dict:
    try:
        return jwt.decode(
            token,
            secret,
            algorithms=[algorithm]
        )
    except ExpiredSignatureError:
        raise ExpiredTokenError()
    except JWTError:
        raise InvalidTokenError()
