from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.handlers.auth_service import get_current_user_from_access_token
from app.core.handlers.follow_service import (
    follow_user,
    get_follow_status,
    list_followers,
    list_following,
    unfollow_user,
)
from app.core.schemas.follow_schema import FollowAction, FollowResponse, FollowStatusResponse
from app.core.schemas.token_schema import AuthMessageResponse

router = APIRouter(prefix="/follows", tags=["follows"])
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


@router.post("", response_model=FollowResponse)
def create_follow(payload: FollowAction, current_user: dict = Depends(get_current_user)):
    try:
        return follow_user(int(current_user["id"]), payload.following_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/user/{following_id}", response_model=AuthMessageResponse)
def delete_follow(following_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return unfollow_user(int(current_user["id"]), following_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/me/following", response_model=list[FollowResponse])
def get_my_following(current_user: dict = Depends(get_current_user)):
    try:
        return list_following(int(current_user["id"]))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/user/{user_id}/followers", response_model=list[FollowResponse])
def get_user_followers(user_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return list_followers(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/user/{user_id}/following", response_model=list[FollowResponse])
def get_user_following(user_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return list_following(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/user/{following_id}/status", response_model=FollowStatusResponse)
def get_status(following_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return get_follow_status(int(current_user["id"]), following_id)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
