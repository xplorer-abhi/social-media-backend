from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class PostCreate(BaseModel):
	content: str = Field(min_length=1)
	image_url: str | None = Field(default=None, max_length=2048)


class PostUpdate(BaseModel):
	content: str = Field(min_length=1)
	image_url: str | None = Field(default=None, max_length=2048)


class PostResponse(BaseModel):
	id: str
	user_id: str
	content: str
	image_url: str | None
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)
