from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LikeAction(BaseModel):
    post_id: str


class LikeResponse(BaseModel):
    id: str
    post_id: str
    user_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LikeCountResponse(BaseModel):
    post_id: str
    likes_count: int = Field(ge=0)
