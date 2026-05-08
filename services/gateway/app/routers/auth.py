from fastapi import APIRouter
from pydantic import BaseModel
from ..dependencies.auth import create_token

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    user_id: int
    # В реальном проекте здесь был бы пароль, но для демо — только user_id


@router.post("/login")
async def login(request: LoginRequest):
    # В реальном проекте: проверить пароль, найти пользователя в БД
    token = create_token(request.user_id)
    return {"access_token": token, "token_type": "bearer"}
