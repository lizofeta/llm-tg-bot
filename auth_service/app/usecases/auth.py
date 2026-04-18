from app.core.exceptions import ( 
    UserAlreadyExistsError,
    InvalidCredentialsError, 
    InvalidTokenError,
    UserNotFoundError
)
from app.repositories.users import UserStorage
from app.db.models import User
from app.core.config import Settings
from app.core.security import (
    hash_password,
    verify_password,
    create_access_token,
    decode_token
)


class AuthUseCase:
    def __init__(
            self, 
            users_repo: UserStorage,
            settings: Settings
        ) -> None:
        self._users_repo = users_repo
        self._settings = settings
    
    async def register(
            self,
            email: str,
            password: str
    ) -> User:
        # Проверка на занятый email
        existing_user = await self._users_repo.get_user_by_email(email)
        if existing_user:
            raise UserAlreadyExistsError()

        # хеширование пароля и создание пользователя в БД
        hashed_pwd = hash_password(password)
        user = await self._users_repo.create_user(
            email,
            hashed_pwd
        )
        return user
    
    async def login(
            self,
            email: str,
            password: str
    ) -> str:
        # Проверка на существование пользователя с указанным email:
        user = await self._users_repo.get_user_by_email(email)
        if user is None:
            raise InvalidCredentialsError()
        
        # Проверка на правильность введенного пароля:
        hashed_pwd = user.password_hash
        if not verify_password(plain_password=password, hashed_password=hashed_pwd):
            raise InvalidCredentialsError()
        
        return create_access_token(
            data={
                "sub": str(user.id),
                "role": user.role
            },
            expire_minutes=self._settings.access_token_expire_minutes,
            secret=self._settings.jwt_secret,
            algorithm=self._settings.jwt_alg
        )
    
    async def me(self, token: str) -> User:
        payload = decode_token(
            token=token,
            secret=self._settings.jwt_secret,
            algorithm=self._settings.jwt_alg
        )

        user_id = payload.get("sub")

        if user_id is None:
            raise InvalidTokenError()
        
        user = await self._users_repo.get_user_by_id(int(user_id))
        if user is None:
            raise UserNotFoundError()

        return user
        
