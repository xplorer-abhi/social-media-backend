from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
	username: str = Field(min_length=3, max_length=50)
	email: str = Field(min_length=5, max_length=255)
	password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
	email: str = Field(min_length=5, max_length=255)
	password: str = Field(min_length=8, max_length=128)


class UserProfileUpdate(BaseModel):
	bio: str | None = Field(default=None, max_length=1000)
	profile_picture: str | None = Field(default=None, max_length=2048)
	is_active: bool = True


class UserResponse(BaseModel):
	id: int
	username: str
	email: str
	bio: str | None
	profile_picture: str | None
	is_active: bool
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
	id: int
	username: str
	email: str
	is_active: bool
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)
