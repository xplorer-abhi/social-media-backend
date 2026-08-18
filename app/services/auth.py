from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.handlers.auth_service import (
	get_current_user_from_access_token,
	login_user,
	logout_user,
	refresh_login,
	register_user,
)
from app.core.schemas.token_schema import AuthMessageResponse, RefreshTokenRequest, TokenPairResponse
from app.core.schemas.user_schema import UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
bearer_scheme = HTTPBearer(auto_error=False)


def _extract_bearer_token(
	credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
) -> str:
	if credentials is None or credentials.scheme.lower() != "bearer":
		raise HTTPException(
			status_code=status.HTTP_401_UNAUTHORIZED,
			detail="Missing or invalid authorization header",
		)
	return credentials.credentials


def get_current_user(token: str = Depends(_extract_bearer_token)) -> dict:
	try:
		return get_current_user_from_access_token(token)
	except ValueError as exc:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc)) from exc


@router.post("/register", response_model=UserResponse)
def register(payload: UserCreate):
	try:
		return register_user(payload)
	except ValueError as exc:
		raise HTTPException(status_code=400, detail=str(exc)) from exc
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/login", response_model=TokenPairResponse)
def login(payload: UserLogin):
	try:
		return login_user(payload)
	except ValueError as exc:
		raise HTTPException(status_code=401, detail=str(exc)) from exc
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/refresh", response_model=TokenPairResponse)
def refresh(payload: RefreshTokenRequest):
	try:
		return refresh_login(payload)
	except ValueError as exc:
		raise HTTPException(status_code=401, detail=str(exc)) from exc
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.post("/logout", response_model=AuthMessageResponse)
def logout(payload: RefreshTokenRequest):
	try:
		return logout_user(payload)
	except Exception as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/me", response_model=UserResponse)
def me(current_user: dict = Depends(get_current_user)):
	return current_user
