from app.core.schemas.post_schema import PostCreate, PostUpdate
from app.models.post_model import (
    delete_post,
    fetch_post_by_id,
    fetch_posts_by_user,
    insert_post,
    update_post,
)
from app.models.user_model import fetch_user_by_id


def _post_row_to_dict(post_row: tuple) -> dict:
    return {
        "id": post_row[0],
        "user_id": post_row[1],
        "content": post_row[2],
        "image_url": post_row[3],
        "created_at": post_row[4],
        "updated_at": post_row[5],
    }


def create_post_for_user(user_id: str, payload: PostCreate) -> dict:
    user_row = fetch_user_by_id(user_id)
    if user_row is None:
        raise ValueError("User does not exist")

    post_id = insert_post(user_id=user_id, content=payload.content, image_url=payload.image_url)
    post_row = fetch_post_by_id(post_id)
    if post_row is None:
        raise RuntimeError("Post created but could not be fetched")

    return _post_row_to_dict(post_row)


def get_post(post_id: str) -> dict:
    post_row = fetch_post_by_id(post_id)
    if post_row is None:
        raise ValueError("Post not found")

    return _post_row_to_dict(post_row)


def list_posts_by_user(user_id: str) -> list[dict]:
    user_row = fetch_user_by_id(user_id)
    if user_row is None:
        raise ValueError("User not found")

    posts = fetch_posts_by_user(user_id)
    return [_post_row_to_dict(post) for post in posts]


def update_post_for_user(user_id: str, post_id: str, payload: PostUpdate) -> dict:
    post_row = fetch_post_by_id(post_id)
    if post_row is None:
        raise ValueError("Post not found")

    post_owner_id = str(post_row[1])
    if post_owner_id != user_id:
        raise PermissionError("You are not allowed to edit this post")

    update_post(post_id=post_id, content=payload.content, image_url=payload.image_url)
    updated_post_row = fetch_post_by_id(post_id)
    if updated_post_row is None:
        raise RuntimeError("Post updated but could not be fetched")

    return _post_row_to_dict(updated_post_row)


def delete_post_for_user(user_id: str, post_id: str) -> dict[str, str]:
    post_row = fetch_post_by_id(post_id)
    if post_row is None:
        raise ValueError("Post not found")

    post_owner_id = str(post_row[1])
    if post_owner_id != user_id:
        raise PermissionError("You are not allowed to delete this post")

    delete_post(post_id)
    return {"message": "Post deleted successfully"}
