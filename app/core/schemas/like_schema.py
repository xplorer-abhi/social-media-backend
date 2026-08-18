from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class LikeAction(BaseModel):
    post_id: int = Field(gt=0)


class LikeResponse(BaseModel):
    id: int
    post_id: int
    user_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class LikeCountResponse(BaseModel):
    post_id: int
    likes_count: int = Field(ge=0)
