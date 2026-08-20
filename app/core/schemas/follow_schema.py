from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class FollowAction(BaseModel):
    following_id: str


class FollowResponse(BaseModel):
    id: str
    follower_id: str
    following_id: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class FollowStatusResponse(BaseModel):
    follower_id: str
    following_id: str
    is_following: bool
