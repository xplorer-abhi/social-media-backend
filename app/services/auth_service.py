from datetime import UTC, datetime

from app.models.base import create_all_tables
from app.models.post_model import fetch_post_by_id, insert_post
from app.models.refresh_token_model import (
	delete_expired_refresh_tokens,
	delete_refresh_token,
	fetch_refresh_token,
	insert_refresh_token,
)
from app.models.user_model import fetch_user_by_email, fetch_user_by_id, insert_user
from app.schemas.post_schema import PostCreate
from app.schemas.token_schema import RefreshTokenRequest
from app.schemas.user_schema import UserCreate, UserLogin
from app.utils.hashing import hash_password, verify_password
from app.utils.tokens import create_access_token, create_refresh_token, decode_token


def _user_row_to_dict(row: tuple) -> dict:
	return {
		"id": row[0],
		"username": row[1],
		"email": row[2],
		"bio": row[3],
		"profile_picture": row[4],
		"is_active": row[5],
		"created_at": row[6],
		"updated_at": row[7],
	}


def _issue_token_pair(user_id: int) -> dict[str, str]:
	access_token = create_access_token(user_id)
	refresh_token, refresh_expires_at = create_refresh_token(user_id)
	insert_refresh_token(user_id=user_id, token=refresh_token, expires_at=refresh_expires_at)
	return {
		"access_token": access_token,
		"refresh_token": refresh_token,
		"token_type": "bearer",
	}


def bootstrap_tables() -> dict[str, str]:
	create_all_tables()
	return {"status": "ok", "message": "All tables ensured successfully"}


def register_user(payload: UserCreate) -> dict:
	existing_user = fetch_user_by_email(payload.email)
	if existing_user is not None:
		raise ValueError("Email already registered")

	password_hash = hash_password(payload.password)
	user_id = insert_user(payload.username, payload.email, password_hash)
	created_user = fetch_user_by_id(user_id)
	if created_user is None:
		raise RuntimeError("User created but could not be fetched")

	return _user_row_to_dict(created_user)


def login_user(payload: UserLogin) -> dict[str, str]:
	user_row = fetch_user_by_email(payload.email)
	if user_row is None:
		raise ValueError("Invalid email or password")

	password_hash = user_row[3]
	if not verify_password(payload.password, password_hash):
		raise ValueError("Invalid email or password")

	return _issue_token_pair(int(user_row[0]))


def refresh_login(payload: RefreshTokenRequest) -> dict[str, str]:
	delete_expired_refresh_tokens()
	stored_row = fetch_refresh_token(payload.refresh_token)
	if stored_row is None:
		raise ValueError("Invalid refresh token")

	token_payload = decode_token(payload.refresh_token)
	if token_payload.get("type") != "refresh":
		raise ValueError("Invalid refresh token type")

	token_user_id = int(token_payload.get("sub", "0"))
	stored_user_id = int(stored_row[1])
	if token_user_id != stored_user_id:
		raise ValueError("Refresh token user mismatch")

	stored_expiry = stored_row[4]
	if stored_expiry.tzinfo is None:
		stored_expiry = stored_expiry.replace(tzinfo=UTC)
	if stored_expiry <= datetime.now(UTC):
		delete_refresh_token(payload.refresh_token)
		raise ValueError("Refresh token expired")

	delete_refresh_token(payload.refresh_token)
	return _issue_token_pair(token_user_id)


def logout_user(payload: RefreshTokenRequest) -> dict[str, str]:
	stored_row = fetch_refresh_token(payload.refresh_token)
	if stored_row is not None:
		delete_refresh_token(payload.refresh_token)
	return {"message": "Logged out successfully"}


def get_current_user_from_access_token(token: str) -> dict:
	token_payload = decode_token(token)
	if token_payload.get("type") != "access":
		raise ValueError("Invalid access token type")

	user_id = int(token_payload.get("sub", "0"))
	if user_id <= 0:
		raise ValueError("Invalid access token subject")

	user_row = fetch_user_by_id(user_id)
	if user_row is None:
		raise ValueError("User not found")

	return _user_row_to_dict(user_row)


def create_post_for_user(user_id: int, payload: PostCreate) -> dict:
	user_row = fetch_user_by_id(user_id)
	if user_row is None:
		raise ValueError("User does not exist")

	post_id = insert_post(user_id=user_id, content=payload.content, image_url=payload.image_url)
	post_row = fetch_post_by_id(post_id)
	if post_row is None:
		raise RuntimeError("Post created but could not be fetched")

	return {
		"id": post_row[0],
		"user_id": post_row[1],
		"content": post_row[2],
		"image_url": post_row[3],
		"created_at": post_row[4],
		"updated_at": post_row[5],
	}
