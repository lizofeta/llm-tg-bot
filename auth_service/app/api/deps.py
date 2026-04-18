from typing import Annotated
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.core.config import get_settings, Settings
from app.usecases.auth import AuthUseCase
from app.repositories.users import UserStorage
from app.db.models import User

# зависимость для получения сессии БД
DBDep = Annotated[AsyncSession, Depends(get_db)]

# зависимость для получения конфигурационных настроек 
SettingsDep = Annotated[Settings, Depends(get_settings)]

# фабрика и зависимость получения репозитория пользователей
def get_users_repo(db: DBDep) -> UserStorage:
    return UserStorage(db=db)

UsersRepoDep = Annotated[UserStorage, Depends(get_users_repo)]

# usecases 
def get_auth_usecase(
        users_repo: UsersRepoDep,
        settings: SettingsDep
) -> AuthUseCase:
    return AuthUseCase(users_repo, settings)

AuthUseCaseDep = Annotated[AuthUseCase, Depends(get_auth_usecase)]

# OAuth2 token
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
OAuthDep = Annotated[str, Depends(oauth2_scheme)]

# OAuth2 password request form
OAuth2RequestFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]

# current user
async def get_current_user(
        token: OAuthDep,
        auth_uc: AuthUseCaseDep
) -> User:
    current_user = await auth_uc.me(token)
    return current_user

CurrentUserDep = Annotated[User, Depends(get_current_user)]

def get_current_user_id(
        current_user: CurrentUserDep
) -> int:
    return current_user.id

CurrentUserIDDep = Annotated[int, Depends(get_current_user_id)]
