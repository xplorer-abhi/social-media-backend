from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


NotificationType = Literal["like", "comment", "follow", "system"]


class NotificationCreate(BaseModel):
    user_id: int = Field(gt=0)
    type: NotificationType
    message: str = Field(min_length=1, max_length=2000)


class NotificationResponse(BaseModel):
    id: int
    user_id: int
    type: str
    message: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class NotificationMarkRead(BaseModel):
    notification_id: int = Field(gt=0)
