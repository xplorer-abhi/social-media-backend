from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
	post_id: int = Field(gt=0)
	content: str = Field(min_length=1)


class CommentUpdate(BaseModel):
	content: str = Field(min_length=1)


class CommentResponse(BaseModel):
	id: int
	post_id: int
	user_id: int
	content: str
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
