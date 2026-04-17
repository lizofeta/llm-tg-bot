from pydantic import BaseModel, EmailStr
from app.core.enums import Role
from datetime import datetime

class UserPublic(BaseModel):
    id: int 
    email: EmailStr
    role: Role 
    created_at: datetime
    model_config = {"from_attributes": True}