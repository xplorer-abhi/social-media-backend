from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.handlers.auth_service import get_current_user_from_access_token
from app.core.handlers.like_service import get_like_count, like_post_for_user, list_likes_by_post, unlike_post_for_user
from app.core.schemas.like_schema import LikeAction, LikeCountResponse, LikeResponse
from app.core.schemas.token_schema import AuthMessageResponse

router = APIRouter(prefix="/likes", tags=["likes"])
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


@router.post("", response_model=LikeResponse)
def like_post(payload: LikeAction, current_user: dict = Depends(get_current_user)):
    try:
        return like_post_for_user(int(current_user["id"]), payload.post_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/post/{post_id}", response_model=AuthMessageResponse)
def unlike_post(post_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return unlike_post_for_user(int(current_user["id"]), post_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/post/{post_id}", response_model=list[LikeResponse])
def get_likes_by_post(post_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return list_likes_by_post(post_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/post/{post_id}/count", response_model=LikeCountResponse)
def get_post_like_count(post_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return get_like_count(post_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
