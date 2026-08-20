from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
	post_id: str
	content: str = Field(min_length=1)


class CommentUpdate(BaseModel):
	content: str = Field(min_length=1)


class CommentResponse(BaseModel):
	id: str
	post_id: str
	user_id: str
	content: str
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
