from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.handlers.auth_service import get_current_user_from_access_token
from app.core.handlers.post_service import (
    create_post_for_user,
    delete_post_for_user,
    get_post,
    list_posts_by_user,
    update_post_for_user,
)
from app.core.schemas.post_schema import PostCreate, PostResponse, PostUpdate
from app.core.schemas.token_schema import AuthMessageResponse

router = APIRouter(prefix="/posts", tags=["posts"])
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


@router.post("", response_model=PostResponse)
def create_post(payload: PostCreate, current_user: dict = Depends(get_current_user)):
    try:
        return create_post_for_user(int(current_user["id"]), payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/me", response_model=list[PostResponse])
def get_my_posts(current_user: dict = Depends(get_current_user)):
    try:
        return list_posts_by_user(int(current_user["id"]))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/user/{user_id}", response_model=list[PostResponse])
def get_posts_by_user(user_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return list_posts_by_user(user_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{post_id}", response_model=PostResponse)
def get_post_by_id(post_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return get_post(post_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, payload: PostUpdate, current_user: dict = Depends(get_current_user)):
    try:
        return update_post_for_user(int(current_user["id"]), post_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{post_id}", response_model=AuthMessageResponse)
def delete_post(post_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return delete_post_for_user(int(current_user["id"]), post_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


