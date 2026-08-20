from datetime import UTC, datetime

from app.core.schemas.token_schema import RefreshTokenRequest
from app.core.schemas.user_schema import UserCreate, UserLogin, UserPasswordChange, UserProfileUpdate
from app.models.follow_model import count_followers, count_following
from app.models.post_model import count_posts_by_user
from app.models.refresh_token_model import (
	delete_expired_refresh_tokens,
	delete_refresh_token,
	fetch_refresh_token,
	insert_refresh_token,
)
from app.models.user_model import (
	fetch_user_by_email,
	fetch_user_by_id,
	fetch_user_by_username,
	fetch_user_credentials_by_username,
	fetch_user_password_hash,
	insert_user,
	search_users_by_username,
	update_user_password,
	update_user_profile,
)
from app.utils.hashing import hash_password, hash_token, verify_password
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


def _issue_token_pair(user_id: str) -> dict[str, str]:
	access_token = create_access_token(user_id)
	refresh_token, refresh_expires_at = create_refresh_token(user_id)
	insert_refresh_token(user_id=user_id, token_hash=hash_token(refresh_token), expires_at=refresh_expires_at)
	return {
		"access_token": access_token,
		"refresh_token": refresh_token,
		"token_type": "bearer",
	}


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
	identifier = payload.identifier.strip()
	user_row = fetch_user_by_email(identifier) if "@" in identifier else fetch_user_credentials_by_username(identifier)
	if user_row is None:
		raise ValueError("Invalid credentials")

	password_hash = user_row[3]
	if not verify_password(payload.password, password_hash):
		raise ValueError("Invalid credentials")

	return _issue_token_pair(str(user_row[0]))


def refresh_login(payload: RefreshTokenRequest) -> dict[str, str]:
	delete_expired_refresh_tokens()
	token_hash = hash_token(payload.refresh_token)
	stored_row = fetch_refresh_token(token_hash)
	if stored_row is None:
		raise ValueError("Invalid refresh token")

	token_payload = decode_token(payload.refresh_token)
	if token_payload.get("type") != "refresh":
		raise ValueError("Invalid refresh token type")

	token_user_id = str(token_payload.get("sub", ""))
	stored_user_id = str(stored_row[1])
	if token_user_id != stored_user_id:
		raise ValueError("Refresh token user mismatch")

	stored_expiry = stored_row[4]
	if stored_expiry.tzinfo is None:
		stored_expiry = stored_expiry.replace(tzinfo=UTC)
	if stored_expiry <= datetime.now(UTC):
		delete_refresh_token(token_hash)
		raise ValueError("Refresh token expired")

	delete_refresh_token(token_hash)
	return _issue_token_pair(token_user_id)


def logout_user(payload: RefreshTokenRequest) -> dict[str, str]:
	token_hash = hash_token(payload.refresh_token)
	stored_row = fetch_refresh_token(token_hash)
	if stored_row is not None:
		delete_refresh_token(token_hash)
	return {"message": "Logged out successfully"}


def get_current_user_from_access_token(token: str) -> dict:
	token_payload = decode_token(token)
	if token_payload.get("type") != "access":
		raise ValueError("Invalid access token type")

	user_id = str(token_payload.get("sub", ""))
	if not user_id:
		raise ValueError("Invalid access token subject")

	user_row = fetch_user_by_id(user_id)
	if user_row is None:
		raise ValueError("User not found")

	return _user_row_to_dict(user_row)


def update_profile_for_user(user_id: str, payload: UserProfileUpdate) -> dict:
	user_row = fetch_user_by_id(user_id)
	if user_row is None:
		raise ValueError("User not found")

	new_username = payload.username if payload.username is not None else user_row[1]
	if new_username != user_row[1]:
		existing_user = fetch_user_by_username(new_username)
		if existing_user is not None:
			raise ValueError("Username already taken")

	# is_active is not user-editable; preserve its current value here.
	update_user_profile(
		user_id=user_id,
		username=new_username,
		bio=payload.bio,
		profile_picture=payload.profile_picture,
		is_active=user_row[5],
	)
	updated_user = fetch_user_by_id(user_id)
	if updated_user is None:
		raise RuntimeError("Profile updated but could not be fetched")

	return _user_row_to_dict(updated_user)


def change_password_for_user(user_id: str, payload: UserPasswordChange) -> dict[str, str]:
	current_password_hash = fetch_user_password_hash(user_id)
	if current_password_hash is None:
		raise ValueError("User not found")

	if not verify_password(payload.current_password, current_password_hash):
		raise ValueError("Current password is incorrect")

	new_password_hash = hash_password(payload.new_password)
	update_user_password(user_id, new_password_hash)
	return {"message": "Password changed successfully"}


def search_users(search_term: str) -> list[dict]:
	search_term = search_term.strip()
	if not search_term:
		return []

	user_rows = search_users_by_username(search_term)
	return [
		{
			"id": row[0],
			"username": row[1],
			"bio": row[2],
			"profile_picture": row[3],
		}
		for row in user_rows
	]


def get_my_profile(user_id: str) -> dict:
	user_row = fetch_user_by_id(user_id)
	if user_row is None:
		raise ValueError("User not found")

	user_dict = _user_row_to_dict(user_row)
	user_dict["followers_count"] = count_followers(user_id)
	user_dict["following_count"] = count_following(user_id)
	return user_dict


def get_public_profile(user_id: str) -> dict:
	user_row = fetch_user_by_id(user_id)
	if user_row is None:
		raise ValueError("User not found")

	return {
		"id": user_row[0],
		"username": user_row[1],
		"bio": user_row[3],
		"profile_picture": user_row[4],
		"followers_count": count_followers(user_id),
		"following_count": count_following(user_id),
		"posts_count": count_posts_by_user(user_id),
		"created_at": user_row[6],
	}
