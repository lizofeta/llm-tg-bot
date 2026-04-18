from fastapi import APIRouter, status

from app.schemas.user import UserPublic
from app.schemas.auth import RegisterRequest, TokenResponse

from app.api.deps import AuthUseCaseDep, OAuth2RequestFormDep, CurrentUserDep

auth_router = APIRouter(prefix="/auth", tags=["auth"])

@auth_router.post(
    "/register",
    response_model=UserPublic,
    status_code=status.HTTP_201_CREATED
)
async def register(
    data: RegisterRequest,
    auth_uc: AuthUseCaseDep
) -> UserPublic:
    return await auth_uc.register(data.email, data.password)

@auth_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK
)
async def login(
    form_data: OAuth2RequestFormDep,
    auth_uc: AuthUseCaseDep
) -> TokenResponse:
    token =  await auth_uc.login(form_data.username, form_data.password)
    return TokenResponse(access_token=token)

@auth_router.get(
    "/me",
    response_model=UserPublic,
    status_code=status.HTTP_200_OK
)
async def me(user: CurrentUserDep) -> UserPublic:
    return user
