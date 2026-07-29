from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FollowAction(BaseModel):
    following_id: int = Field(gt=0)


class FollowResponse(BaseModel):
    id: int
    follower_id: int
    following_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
