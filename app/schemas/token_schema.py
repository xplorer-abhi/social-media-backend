from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TokenPairResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(min_length=20)


class RefreshTokenResponse(BaseModel):
    id: int
    user_id: int
    token: str
    created_at: datetime
    expires_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AuthMessageResponse(BaseModel):
    message: str
