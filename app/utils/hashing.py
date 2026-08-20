import bcrypt
import hashlib


def hash_password(password: str) -> str:
	password_bytes = password.encode("utf-8")
	hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt())
	return hashed.decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
	password_bytes = password.encode("utf-8")
	password_hash_bytes = password_hash.encode("utf-8")
	return bcrypt.checkpw(password_bytes, password_hash_bytes)


def hash_token(token: str) -> str:
	# Refresh tokens are high-entropy already, so a fast deterministic hash (not bcrypt) is enough and allows exact-match lookups.
	return hashlib.sha256(token.encode("utf-8")).hexdigest()
