from app.core.schemas.comment_schema import CommentCreate, CommentUpdate
from app.models.comment_model import (
    delete_comment,
    fetch_comment_by_id,
    fetch_comments_by_post,
    insert_comment,
    update_comment,
)
from app.models.post_model import fetch_post_by_id
from app.models.user_model import fetch_user_by_id


def _comment_row_to_dict(comment_row: tuple) -> dict:
    return {
        "id": comment_row[0],
        "post_id": comment_row[1],
        "user_id": comment_row[2],
        "content": comment_row[3],
        "created_at": comment_row[4],
    }



def create_comment_for_user(user_id: int, payload: CommentCreate) -> dict:
    user_row = fetch_user_by_id(user_id)
    if user_row is None:
        raise ValueError("User does not exist")

    post_row = fetch_post_by_id(payload.post_id)
    if post_row is None:
        raise ValueError("Post not found")

    comment_id = insert_comment(payload.post_id, user_id, payload.content)
    comment_row = fetch_comment_by_id(comment_id)
    if comment_row is None:
        raise RuntimeError("Comment created but could not be fetched")

    return _comment_row_to_dict(comment_row)



def get_comment(comment_id: int) -> dict:
    comment_row = fetch_comment_by_id(comment_id)
    if comment_row is None:
        raise ValueError("Comment not found")

    return _comment_row_to_dict(comment_row)



def list_comments_by_post(post_id: int) -> list[dict]:
    post_row = fetch_post_by_id(post_id)
    if post_row is None:
        raise ValueError("Post not found")

    comments = fetch_comments_by_post(post_id)
    return [_comment_row_to_dict(comment) for comment in comments]



def update_comment_for_user(user_id: int, comment_id: int, payload: CommentUpdate) -> dict:
    comment_row = fetch_comment_by_id(comment_id)
    if comment_row is None:
        raise ValueError("Comment not found")

    comment_owner_id = int(comment_row[2])
    if comment_owner_id != user_id:
        raise PermissionError("You are not allowed to edit this comment")

    update_comment(comment_id, payload.content)
    updated_comment_row = fetch_comment_by_id(comment_id)
    if updated_comment_row is None:
        raise RuntimeError("Comment updated but could not be fetched")

    return _comment_row_to_dict(updated_comment_row)



def delete_comment_for_user(user_id: int, comment_id: int) -> dict[str, str]:
    comment_row = fetch_comment_by_id(comment_id)
    if comment_row is None:
        raise ValueError("Comment not found")

    comment_owner_id = int(comment_row[2])
    if comment_owner_id != user_id:
        raise PermissionError("You are not allowed to delete this comment")

    delete_comment(comment_id)
    return {"message": "Comment deleted successfully"}
