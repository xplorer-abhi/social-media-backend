from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.handlers.auth_service import get_current_user_from_access_token
from app.core.handlers.comment_service import (
    create_comment_for_user,
    delete_comment_for_user,
    get_comment,
    list_comments_by_post,
    update_comment_for_user,
)
from app.core.schemas.comment_schema import CommentCreate, CommentResponse, CommentUpdate
from app.core.schemas.token_schema import AuthMessageResponse

router = APIRouter(prefix="/comments", tags=["comments"])
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


@router.post("", response_model=CommentResponse)
def create_comment(payload: CommentCreate, current_user: dict = Depends(get_current_user)):
    try:
        return create_comment_for_user(int(current_user["id"]), payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/post/{post_id}", response_model=list[CommentResponse])
def get_comments_by_post(post_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return list_comments_by_post(post_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get("/{comment_id}", response_model=CommentResponse)
def get_comment_by_id(comment_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return get_comment(comment_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.put("/{comment_id}", response_model=CommentResponse)
def update_comment(comment_id: int, payload: CommentUpdate, current_user: dict = Depends(get_current_user)):
    try:
        return update_comment_for_user(int(current_user["id"]), comment_id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.delete("/{comment_id}", response_model=AuthMessageResponse)
def delete_comment(comment_id: int, current_user: dict = Depends(get_current_user)):
    try:
        return delete_comment_for_user(int(current_user["id"]), comment_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except PermissionError as exc:
        raise HTTPException(status_code=403, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc
