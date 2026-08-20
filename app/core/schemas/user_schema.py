from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserCreate(BaseModel):
	username: str = Field(min_length=3, max_length=50)
	email: str = Field(min_length=5, max_length=255)
	password: str = Field(min_length=8, max_length=128)


class UserLogin(BaseModel):
	identifier: str = Field(min_length=3, max_length=255, description="Email or username")
	password: str = Field(min_length=8, max_length=128)


class UserProfileUpdate(BaseModel):
	username: str | None = Field(default=None, min_length=3, max_length=50)
	bio: str | None = Field(default=None, max_length=1000)
	profile_picture: str | None = Field(default=None, max_length=2048)


class UserPasswordChange(BaseModel):
	current_password: str = Field(min_length=8, max_length=128)
	new_password: str = Field(min_length=8, max_length=128)


class UserResponse(BaseModel):
	id: str
	username: str
	email: str
	bio: str | None
	profile_picture: str | None
	is_active: bool
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)


class UserListResponse(BaseModel):
	id: str
	username: str
	email: str
	is_active: bool
	created_at: datetime
	updated_at: datetime

	model_config = ConfigDict(from_attributes=True)


class UserSearchResult(BaseModel):
	id: str
	username: str
	bio: str | None
	profile_picture: str | None

	model_config = ConfigDict(from_attributes=True)


class UserProfileResponse(BaseModel):
	id: str
	username: str
	email: str
	bio: str | None
	profile_picture: str | None
	followers_count: int
	following_count: int
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)


class PublicUserProfileResponse(BaseModel):
	id: str
	username: str
	bio: str | None
	profile_picture: str | None
	followers_count: int
	following_count: int
	posts_count: int
	created_at: datetime

	model_config = ConfigDict(from_attributes=True)
