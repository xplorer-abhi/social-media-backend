from psycopg2 import IntegrityError

from app.models.like_model import add_like, count_likes_by_post, fetch_like, fetch_likes_by_post, remove_like
from app.models.post_model import fetch_post_by_id
from app.models.user_model import fetch_user_by_id


def _like_row_to_dict(like_row: tuple) -> dict:
    return {
        "id": like_row[0],
        "post_id": like_row[1],
        "user_id": like_row[2],
        "created_at": like_row[3],
    }



def like_post_for_user(user_id: str, post_id: str) -> dict:
    user_row = fetch_user_by_id(user_id)
    if user_row is None:
        raise ValueError("User does not exist")

    post_row = fetch_post_by_id(post_id)
    if post_row is None:
        raise ValueError("Post not found")

    existing_like = fetch_like(post_id, user_id)
    if existing_like is not None:
        raise ValueError("Post already liked")

    try:
        like_id = add_like(post_id, user_id)
    except IntegrityError as exc:
        raise ValueError("Post already liked") from exc

    like_row = fetch_like(post_id, user_id)
    if like_row is None:
        raise RuntimeError("Like created but could not be fetched")

    return _like_row_to_dict(like_row)



def unlike_post_for_user(user_id: str, post_id: str) -> dict[str, str]:
    existing_like = fetch_like(post_id, user_id)
    if existing_like is None:
        raise ValueError("Like not found")

    remove_like(post_id, user_id)
    return {"message": "Post unliked successfully"}



def list_likes_by_post(post_id: str) -> list[dict]:
    post_row = fetch_post_by_id(post_id)
    if post_row is None:
        raise ValueError("Post not found")

    likes = fetch_likes_by_post(post_id)
    return [_like_row_to_dict(like) for like in likes]



def get_like_count(post_id: str) -> dict:
    post_row = fetch_post_by_id(post_id)
    if post_row is None:
        raise ValueError("Post not found")

    return {"post_id": post_id, "likes_count": count_likes_by_post(post_id)}
